from pathlib import Path


OUTPUT_DIR = Path("output")


def output_path(input_path, output=None, suffix="", extension=".md"):
    destination = Path(output) if output else OUTPUT_DIR / f"{Path(input_path).stem}{suffix}{extension}"
    if destination.resolve() == Path(input_path).resolve():
        raise ValueError("Input and output must be different files")
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination


def write_text(destination, text):
    destination.write_text(text, encoding="utf-8")
    return destination
