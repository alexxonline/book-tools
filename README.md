# Book Tools

Utilities for preparing, translating, and generating audiobooks from book text files. These scripts are small helper tools used to download files, clean and convert text, split into chunks, count tokens, translate, and generate audio.

## Repository Structure

- `download_files.py` - Download all files from a Google Cloud Storage bucket to a local folder.
- `convert.py` - (utility) Convert file formats or prepare files for processing.
- `clean.py` - Clean markdown or text files (remove unwanted characters, normalize whitespace).
- `fix_spaces.py` - Fix spacing issues in text files.
- `divide_into_chunks.py` - Split long text files into smaller chunks for processing.
- `count_tokens.py` - Count tokens in text files (useful for pricing and chunking when using LLMs).
- `character_count.py` - Count characters in a file.
- `translate_to_spanish.py` - Translate text files into Spanish.
- `generate_audiobook.py` - Generate short audiobooks from text using a TTS provider.
- `generate_audiobook_long.py` - Generate audiobooks for longer texts (handles chunking and long-run jobs).
- `out_md/` - Output markdown files (processed/translated files).
- `downloaded_files/` - Files downloaded from storage by `download_files.py`.
- `pdfvenv/` - Virtual environment used for running scripts (optional directory; not included in packaging).
- `requirements.txt` - Python dependencies.

## Quickstart

1. Create a Python 3.11+ virtual environment and activate it (macOS / zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. (Optional) If you will download files from Google Cloud Storage, set the service account credentials environment variable. Create or obtain a service account JSON file and set:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

3. Run the scripts as needed. Examples are below.

## Usage Examples

- Download all files from a GCS bucket into `downloaded_files/`:

```bash
python download_files.py
```

- Clean a markdown file (example):

```bash
python clean.py path/to/input.md path/to/output.cleaned.md
```

- Divide a large file into chunks:

```bash
python divide_into_chunks.py path/to/large.md --chunk-size 2000 --out-dir chunks/
```

- Translate a file to Spanish:

```bash
python translate_to_spanish.py path/to/input.md path/to/output_es.md
```

- Generate an audiobook (short):

```bash
python generate_audiobook.py path/to/input.md --out-dir audio/
```

## Environment Variables

- `GOOGLE_APPLICATION_CREDENTIALS` - Path to Google Cloud service account JSON (for `download_files.py`).

## Notes & Tips

- The `download_files.py` script uses the Google Cloud Storage Python client and expects credentials to be configured via the `GOOGLE_APPLICATION_CREDENTIALS` environment variable or through default application credentials.
- If you edit or run TTS scripts that use Google Cloud Text-to-Speech, ensure the corresponding APIs are enabled for your project and credentials have appropriate permissions.
- The `pdfvenv/` directory is included in this repo; prefer creating a new `.venv` for local development to avoid accidentally modifying the committed environment.

## Contributing

Feel free to open issues or PRs to improve scripts, add tests, or make the tools more robust.

## License
TBD