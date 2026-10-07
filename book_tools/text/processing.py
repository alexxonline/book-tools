import re
from pathlib import Path

from book_tools.paths import OUTPUT_DIR, output_path, write_text


def clean_file(input_path, output=None):
    content = Path(input_path).read_text(encoding="utf-8")
    lines = [line.replace("#", "") for line in content.splitlines(keepends=True)
             if not re.fullmatch(r"<!-- (?:Page|Página) \d+ -->", line.strip())]
    return write_text(output_path(input_path, output, ".cleaned"), "".join(lines))


def fix_spaces(input_path, output=None):
    lines = Path(input_path).read_text(encoding="utf-8").splitlines()
    fixed_lines = []
    paragraph = []
    fence = None

    def flush():
        if paragraph:
            fixed_lines.append(" ".join(paragraph))
            paragraph.clear()

    for line in lines:
        stripped = line.strip()
        marker = re.match(r"^(`{3,}|~{3,})", stripped)
        if fence:
            fixed_lines.append(line)
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
        elif marker:
            flush()
            fence = marker[1]
            fixed_lines.append(line)
        elif not stripped:
            flush()
            if fixed_lines and fixed_lines[-1] != "":
                fixed_lines.append("")
        elif line.startswith(("    ", "\t")) or re.match(r"^(#{1,6}\s|[-+*]\s|\d+[.)]\s|>|\||[-*_]{3,}$|={3,}$)", stripped):
            flush()
            fixed_lines.append(line)
        else:
            paragraph.append(stripped)
    flush()
    return write_text(output_path(input_path, output, ".fixed"), "\n".join(fixed_lines).rstrip() + "\n")


def divide_md_into_chunks(input_path, num_chunks=10, out_dir=None):
    if num_chunks < 1:
        raise ValueError("Number of chunks must be positive")
    paragraphs = [paragraph.strip() for paragraph in
                  Path(input_path).read_text(encoding="utf-8").split("\n\n") if paragraph.strip()]
    if not paragraphs:
        raise ValueError("Input contains no paragraphs")
    destination = Path(out_dir) if out_dir else OUTPUT_DIR / f"{Path(input_path).stem}.chunks"
    destination.mkdir(parents=True, exist_ok=True)
    chunk_count = min(num_chunks, len(paragraphs))
    chunk_size, remainder = divmod(len(paragraphs), chunk_count)
    paths = [destination / f"{Path(input_path).stem}.{index + 1}.md" for index in range(chunk_count)]
    if any(path.resolve() == Path(input_path).resolve() for path in paths):
        raise ValueError("Chunk output would overwrite the input")
    start = 0
    for index, path in enumerate(paths):
        end = start + chunk_size + (index < remainder)
        write_text(path, "\n\n".join(paragraphs[start:end]) + "\n")
        start = end
    return paths


def count_characters(input_path):
    return len(Path(input_path).read_text(encoding="utf-8"))


def count_tokens_in_file(input_path, model="gpt-4o"):
    import tiktoken

    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(Path(input_path).read_text(encoding="utf-8"), disallowed_special=()))
