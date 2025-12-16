import os
import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.5-flash"
API_KEY = os.getenv("OPENROUTER_API_KEY")
INPUT_MD = "out_md/meditations_for_mortals.md"
OUTPUT_MD = "out_md/meditations_for_mortals_es.md"

if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable not set.")

def read_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def translate_text(text):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional translator."},
            {"role": "user", "content": f"Translate the following markdown file to Spanish, preserving formatting.\n\n{text}"}
        ]
    }
    response = requests.post(OPENROUTER_URL, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"]

def write_markdown(file_path, text):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    md_text = read_markdown(INPUT_MD)
    translated = translate_text(md_text)
    write_markdown(OUTPUT_MD, translated)
    print(f"Translation complete. Output written to {OUTPUT_MD}")

if __name__ == "__main__":
    main()
