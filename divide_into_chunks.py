import os

def divide_md_into_chunks(md_path, num_chunks=10):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Split by double newlines (paragraphs)
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    total_paragraphs = len(paragraphs)
    chunk_size = total_paragraphs // num_chunks
    remainder = total_paragraphs % num_chunks
    chunks = []
    start = 0
    for i in range(num_chunks):
        end = start + chunk_size + (1 if i < remainder else 0)
        chunk_paragraphs = paragraphs[start:end]
        chunk_content = '\n\n'.join(chunk_paragraphs)
        chunks.append(chunk_content)
        start = end
    # Write chunks to files
    base_name = os.path.splitext(os.path.basename(md_path))[0]
    out_dir = os.path.dirname(md_path)
    for idx, chunk in enumerate(chunks, 1):
        chunk_filename = f"{base_name}.{idx}.md"
        chunk_path = os.path.join(out_dir, chunk_filename)
        with open(chunk_path, 'w', encoding='utf-8') as f:
            f.write(chunk)
    print(f"Divided into {num_chunks} chunks.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python divide_into_chunks.py <md_file_path> [num_chunks]")
        sys.exit(1)
    md_file = sys.argv[1]
    num_chunks = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    divide_md_into_chunks(md_file, num_chunks)
