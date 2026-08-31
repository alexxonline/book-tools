import os, base64, pathlib
from itertools import count
from mistralai import Mistral

PDF_PATH = "four-thousand-weeks.pdf"
OUT_DIR  = pathlib.Path("out_md")
MODEL    = "mistral-ocr-latest"

OUT_DIR.mkdir(parents=True, exist_ok=True)
images_dir = OUT_DIR / "images"
images_dir.mkdir(exist_ok=True)

def pdf_to_data_uri(pdf_path: str) -> str:
    with open(pdf_path, "rb") as f:
        return "data:application/pdf;base64," + base64.b64encode(f.read()).decode()

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
resp = client.ocr.process(
    model=MODEL,
    document={"type": "document_url", "document_url": pdf_to_data_uri(PDF_PATH)},
    include_image_base64=True,
)

img_counter = count(1)  # <- stateful counter, no nonlocal/global needed

def save_image(image_base64: str, image_id: str, page_idx: int) -> str:
    """Save an OCR image and return its path relative to the Markdown file."""
    header, separator, payload = image_base64.partition(",")
    if not separator:
        header = ""
        payload = image_base64

    suffix = pathlib.Path(image_id).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        ext = suffix
    elif "png" in header.lower():
        ext = ".png"
    elif "gif" in header.lower():
        ext = ".gif"
    elif "webp" in header.lower():
        ext = ".webp"
    else:
        ext = ".jpg"

    n = next(img_counter)
    fname = f"page{page_idx:03d}_{n:03d}{ext}"
    (images_dir / fname).write_bytes(base64.b64decode(payload))
    return f"images/{fname}"

md_parts = []

for i, page in enumerate(resp.pages, start=1):
    page_md = page.markdown or ""
    for image in page.images or []:
        if not image.image_base64:
            continue

        path = save_image(image.image_base64, image.id, i)
        # Mistral places the image ID in the Markdown target, for example:
        # ![img-0.jpeg](img-0.jpeg)
        page_md = page_md.replace(f"]({image.id})", f"]({path})")

    md_parts.append(f"\n<!-- Page {i} -->\n\n{page_md.strip()}\n")

out_md = OUT_DIR / (pathlib.Path(PDF_PATH).stem + ".md")
out_md.write_text("# Converted from PDF\n\n" + "".join(md_parts), encoding="utf-8")

print(f"Markdown saved to: {out_md.resolve()}")
print(f"Images saved (if any) to: {images_dir.resolve()}")
