import os
from pathlib import Path

from book_tools.paths import output_path, write_text


def translate_to_spanish(input_path, output=None, model="google/gemini-2.5-flash"):
    import requests

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("Set OPENROUTER_API_KEY before translating")
    destination = output_path(input_path, output, "_es")
    text = Path(input_path).read_text(encoding="utf-8")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": [
            {"role": "system", "content": "You are a professional translator."},
            {"role": "user", "content": f"Translate the following markdown file to Spanish, preserving formatting.\n\n{text}"},
        ]},
        timeout=300,
    )
    response.raise_for_status()
    translated = response.json()["choices"][0]["message"]["content"]
    return write_text(destination, translated)
