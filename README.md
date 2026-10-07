# Book Tools

Python utilities for converting books to Markdown, preparing text, translating
to Spanish, generating audiobooks, and downloading cloud files.

## Setup

Python 3.11 or newer is required. Run these commands from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[all]'
```

Alternatively, install only the features you need:

```bash
pip install -e .              # Text cleaning, spacing, chunking, character counts
pip install -e '.[epub]'      # Local EPUB conversion
pip install -e '.[pdf]'       # Mistral PDF OCR
pip install -e '.[tokens]'    # Token counting
pip install -e '.[translation]' # OpenRouter translation
pip install -e '.[cloud]'     # Google Cloud audio and storage
```

`pip install -r requirements.txt` installs all features. Optional dependencies
are loaded only when their commands run. Importing modules does not read books,
create clients, or invoke paid services.

## Structure

```text
book_tools/
  conversion/   # EPUB and PDF to Markdown
  text/         # Cleaning, spacing, chunking, counting
  translation/  # Spanish translation through OpenRouter
  audio/        # Short and long Google Cloud audiobooks
  storage/      # Google Cloud Storage downloads
  cli.py        # Command definitions
  paths.py      # Shared output handling
output/         # Generated files; contents are gitignored
pyproject.toml  # Package metadata and optional dependencies
```

## Commands

Use `book-tools` after installation, or `python -m book_tools`. Add `--help` to
any group or command to see its arguments.

### Convert books

```bash
book-tools convert epub books/example.epub
book-tools convert epub books/example.epub --output output/custom.md
book-tools convert pdf books/example.pdf
book-tools convert pdf books/example.pdf --model mistral-ocr-latest
```

EPUB conversion runs locally, following the package spine's reading order and
skipping non-linear supplementary documents. Headings, paragraphs, lists,
emphasis, links, and ordinary HTML images are converted to Markdown. Internal
chapter links are rewritten to anchors in the combined file. Embedded images
are saved beside it in `<book>.images/`. External image URLs are retained.
DRM-protected, malformed, and unsupported chapter formats produce an error.
Font obfuscation is allowed because fonts are not needed for Markdown. This
is text conversion, not OCR; image-only pages do not gain searchable text.
EPUB layout, embedded multimedia, and SVG graphics are not reproduced.

PDF conversion uses Mistral OCR and requires `MISTRAL_API_KEY`. It saves image
assets in `<book>.images/` and inserts page comments in the Markdown.

### Prepare and count text

```bash
book-tools text clean output/example.md
book-tools text fix-spaces output/example.cleaned.md
book-tools text chunks output/example.md --num-chunks 10
book-tools text chunks output/example.md --num-chunks 5 --out-dir output/chunks
book-tools text characters output/example.md
book-tools text tokens output/example.md --model gpt-4o
```

Cleaning preserves the original tool's behavior: it removes all `#` characters
and English or Spanish OCR page comments. This produces narration text rather
than preserving Markdown heading syntax. Spacing joins wrapped paragraph lines,
preserves paragraph breaks, and keeps fenced code and structural lines intact.
Chunking distributes paragraphs evenly into the requested number of chunks;
it produces fewer files when there are fewer paragraphs, and rejects empty
input or non-positive counts. Character and token counts print to the terminal.
Token counting may download the tokenizer data on its first run.

### Translate

```bash
export OPENROUTER_API_KEY="your-api-key"
book-tools translate spanish output/example.md
book-tools translate spanish output/example.md --output output/spanish.md
book-tools translate spanish output/example.md --model google/gemini-2.5-flash
```

Translation sends the complete input to OpenRouter in one request. Use the
chunking tool first for books that exceed the selected model's context limit.

### Generate audio

Configure Google Application Default Credentials or set
`GOOGLE_APPLICATION_CREDENTIALS` to your service account JSON path. The tools
respect existing credentials and do not overwrite the environment.

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
book-tools audio short output/example.cleaned.md
book-tools audio short output/example.cleaned.md --output output/example.mp3
book-tools audio long output/example.cleaned.md \
  --project your-project \
  --output-gcs-uri gs://your-bucket/example.wav
```

Both commands accept `--language` and `--voice`; defaults are `es-US` and
`es-US-Chirp3-HD-Erinome`. Short audio produces MP3 and is subject to the
provider's synchronous input limit. Long audio produces LINEAR16/WAV in GCS,
requires an explicit `.wav` URI, and accepts `--location` (default:
`us-central1`) and `--timeout` (default: 3600 seconds). A timeout stops waiting;
the cloud operation may continue. The required Google APIs and bucket
permissions must be configured. Cloud commands and translation incur provider
usage charges.

### Download cloud files

```bash
book-tools storage download your-bucket
book-tools storage download your-bucket --out-dir output/downloads
```

Downloads preserve the bucket's folder structure and skip directory markers.
Paths that would escape the destination folder are rejected.

## Output defaults

Paths are relative to the current working directory. Run from the repository
root to use its gitignored `output/` folder. Output directories are created as
needed. `output/.gitkeep` keeps the empty folder in Git; generated contents are
ignored. Use `--output` for individual files or `--out-dir` for chunks/downloads
to override the defaults. Existing destination files are overwritten; commands
reject using the input file as their output.

| Tool | Default destination |
| --- | --- |
| EPUB/PDF conversion | `output/<book>.md`, `output/<book>.images/` |
| Cleaning | `output/<book>.cleaned.md` |
| Spacing | `output/<book>.fixed.md` |
| Chunking | `output/<book>.chunks/<book>.<number>.md` |
| Translation | `output/<book>_es.md` |
| Short audio | `output/<book>.mp3` |
| Long audio | Explicit Google Cloud Storage URI |
| Downloads | `output/downloads/` |
