import sys
import tiktoken

# Path to the markdown file
md_file_path = "out_md/meditations_for_mortals.md"

# Choose encoding (e.g., for OpenAI models like 'cl100k_base')
encoding = tiktoken.encoding_for_model("gpt-4o")

def count_tokens_in_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    tokens = encoding.encode(text)
    return len(tokens)

if __name__ == "__main__":
    token_count = count_tokens_in_file(md_file_path)
    print(f"Token count: {token_count}")
