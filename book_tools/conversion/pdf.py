import base64
import os
from pathlib import Path
from urllib.parse import quote

from book_tools.paths import output_path, write_text


def pdf_to_markdown(input_path, output=None, model="mistral-ocr-latest"):
    from mistralai.client import Mistral

    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("Set MISTRAL_API_KEY before converting PDFs")
    destination = output_path(input_path, output)
    document = "data:application/pdf;base64," + base64.b64encode(Path(input_path).read_bytes()).decode()
    client = Mistral(api_key=api_key)
    response = client.ocr.process(model=model, document={"type": "document_url", "document_url": document}, include_image_base64=True)
    images_dir = destination.parent / f"{destination.stem}.images"
    parts = []
    image_count = 0
    for page_index, page in enumerate(response.pages, 1):
        markdown = page.markdown or ""
        for image in page.images or []:
            if not image.image_base64:
                continue
            header, separator, payload = image.image_base64.partition(",")
            if not separator:
                header, payload = "", image.image_base64
            suffix = Path(image.id).suffix.lower()
            if suffix not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
                suffix = next((f".{kind}" for kind in ("png", "gif", "webp") if kind in header.lower()), ".jpg")
            image_count += 1
            images_dir.mkdir(parents=True, exist_ok=True)
            name = f"page{page_index:03d}_{image_count:03d}{suffix}"
            (images_dir / name).write_bytes(base64.b64decode(payload))
            markdown = markdown.replace(f"]({image.id})", f"]({quote(images_dir.name + '/' + name)})")
        parts.append(f"<!-- Page {page_index} -->\n\n{markdown.strip()}")
    return write_text(destination, "# Converted from PDF\n\n" + "\n\n".join(parts) + "\n")
