import argparse
import importlib
from pathlib import Path


def file_arguments(parser):
    parser.add_argument("input_path", type=Path, help="Input file")


def output_arguments(parser):
    parser.add_argument("output_positional", nargs="?", type=Path, help="Optional output file")
    parser.add_argument("-o", "--output", type=Path, help="Output file (default: output/)")


def command(subparsers, name, help_text, module, function, extra):
    parser = subparsers.add_parser(name, help=help_text, description=help_text)
    parser.set_defaults(module=module, function=function, extra=extra)
    return parser


def build_parser():
    parser = argparse.ArgumentParser(description="Convert, prepare, translate, and narrate books")
    groups = parser.add_subparsers(dest="group", required=True)
    conversion = groups.add_parser("convert", help="Convert books to Markdown").add_subparsers(dest="command", required=True)
    for name in ("epub", "pdf"):
        child = command(conversion, name, f"Convert {name.upper()} to Markdown", f"book_tools.conversion.{name}", f"{name}_to_markdown", name)
        file_arguments(child)
        output_arguments(child)
        if name == "pdf":
            child.add_argument("--model", default="mistral-ocr-latest")

    text = groups.add_parser("text", help="Prepare and count text").add_subparsers(dest="command", required=True)
    for name, function, description in (
        ("clean", "clean_file", "Remove hash characters and OCR page comments"),
        ("fix-spaces", "fix_spaces", "Join wrapped paragraph lines"),
        ("chunks", "divide_md_into_chunks", "Split paragraphs into balanced chunks"),
        ("characters", "count_characters", "Count Unicode characters"),
        ("tokens", "count_tokens_in_file", "Count tokens for a model"),
    ):
        child = command(text, name, description, "book_tools.text.processing", function, "tokens" if name == "tokens" else None)
        file_arguments(child)
        if name in ("clean", "fix-spaces"):
            output_arguments(child)
        elif name == "chunks":
            child.add_argument("chunks_positional", nargs="?", type=int, help="Optional number of chunks")
            child.add_argument("--num-chunks", type=int, help="Number of chunks (default: 10)")
            child.add_argument("--out-dir", type=Path, help="Output directory (default: output/<book>.chunks/)")
        elif name == "tokens":
            child.add_argument("--model", default="gpt-4o")

    translation = groups.add_parser("translate", help="Translate books").add_subparsers(dest="command", required=True)
    child = command(translation, "spanish", "Translate Markdown to Spanish using OpenRouter", "book_tools.translation.spanish", "translate_to_spanish", "translation")
    file_arguments(child)
    output_arguments(child)
    child.add_argument("--model", default="google/gemini-2.5-flash")

    audio = groups.add_parser("audio", help="Generate audiobooks").add_subparsers(dest="command", required=True)
    for name in ("short", "long"):
        child = command(audio, name, f"Generate a {name} audiobook using Google Cloud", "book_tools.audio.google", "generate_audiobook_long" if name == "long" else "generate_audiobook", "cloud")
        file_arguments(child)
        child.add_argument("--language", default="es-US")
        child.add_argument("--voice", default="es-US-Chirp3-HD-Erinome")
        if name == "short":
            output_arguments(child)
        else:
            child.add_argument("--project", required=True, help="Google Cloud project ID")
            child.add_argument("--output-gcs-uri", required=True, help="gs://bucket/path.wav")
            child.add_argument("--location", default="us-central1")
            child.add_argument("--timeout", type=float, default=3600, help="Operation wait timeout in seconds")

    storage = groups.add_parser("storage", help="Download cloud files").add_subparsers(dest="command", required=True)
    child = command(storage, "download", "Download a Google Cloud Storage bucket", "book_tools.storage.gcs", "download_all_files_from_bucket", "cloud")
    child.add_argument("bucket_name", help="Bucket name without gs://")
    child.add_argument("--out-dir", dest="destination_folder", type=Path, help="Output directory (default: output/downloads/)")
    return parser


def main(argv=None):
    parser = build_parser()
    arguments = vars(parser.parse_args(argv))
    module = arguments.pop("module")
    function = arguments.pop("function")
    extra = arguments.pop("extra")
    arguments.pop("group")
    arguments.pop("command")
    if "output_positional" in arguments:
        positional = arguments.pop("output_positional")
        if positional and arguments["output"]:
            parser.error("Use either the positional output or --output")
        arguments["output"] = arguments["output"] or positional
    if "chunks_positional" in arguments:
        positional = arguments.pop("chunks_positional")
        if positional is not None and arguments["num_chunks"] is not None:
            parser.error("Use either the positional chunk count or --num-chunks")
        arguments["num_chunks"] = arguments["num_chunks"] if arguments["num_chunks"] is not None else (positional if positional is not None else 10)
    if "input_path" in arguments and not arguments["input_path"].is_file():
        parser.error(f"Input file does not exist: {arguments['input_path']}")
    try:
        result = getattr(importlib.import_module(module), function)(**arguments)
    except ImportError as error:
        parser.exit(1, f"Missing dependency: {error}. Install with: pip install '.[{extra or 'all'}]'\n")
    except Exception as error:
        parser.exit(1, f"Error: {error}\n")
    if isinstance(result, list):
        for path in result:
            print(path)
    else:
        print(result)
    return 0
