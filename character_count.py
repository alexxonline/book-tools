# character_count.py
# Counts the number of characters in meditations_for_mortals_es.md

def count_characters(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return len(content)

if __name__ == "__main__":
    filepath = "out_md/meditations_for_mortals_es.md"
    count = count_characters(filepath)
    print(f"Total characters in {filepath}: {count}")
