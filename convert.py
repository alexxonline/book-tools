import os, base64, pathlib, re
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

def save_data_uri_image(data_uri: str, page_idx: int) -> str:
    header, b64 = data_uri.split(",", 1)
    ext = "png" if "png" in header.lower() else "jpg"
    n = next(img_counter)
    fname = f"page{page_idx:03d}_{n:03d}.{ext}"
    (images_dir / fname).write_bytes(base64.b64decode(b64))
    return f"images/{fname}"

md_parts = []
pattern = r'!\[([^\]]*)\]\((data:image/[^)]+)\)'

for i, page in enumerate(resp.pages, start=1):
    def replace(m: re.Match) -> str:
        alt = m.group(1) or ""
        data_uri = m.group(2)
        path = save_data_uri_image(data_uri, i)
        return f'![{alt}]({path})'

    page_md = re.sub(pattern, replace, page.markdown or "")
    md_parts.append(f"\n<!-- Page {i} -->\n\n{page_md.strip()}\n")

out_md = OUT_DIR / (pathlib.Path(PDF_PATH).stem + ".md")
out_md.write_text("# Converted from PDF\n\n" + "".join(md_parts), encoding="utf-8")

print(f"Markdown saved to: {out_md.resolve()}")
print(f"Images saved (if any) to: {images_dir.resolve()}")
