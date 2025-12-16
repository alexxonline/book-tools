#!/usr/bin/env python3
"""
Script to fix bad spaces in a markdown file.
Removes unnecessary blank lines between lines of the same paragraph.
Preserves all words and punctuation.
Writes output to <input>_fixed.md
"""
import sys
import os

def fix_spaces(input_path):
    output_path = input_path.replace('.md', '_fixed.md')
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = []
    paragraph = []
    for line in lines:
        stripped = line.strip()
        # If line is blank
        if stripped == '':
            if paragraph:
                # End of paragraph, join and add
                fixed_lines.append(' '.join(paragraph) + '\n')
                paragraph = []
            else:
                # Multiple blank lines, skip
                continue
        # If line is heading, list, blockquote, or code
        elif (stripped.startswith('#') or
              stripped.startswith('- ') or
              stripped.startswith('>') or
              stripped.startswith('```') or
              stripped.startswith('* ')):
            if paragraph:
                fixed_lines.append(' '.join(paragraph) + '\n')
                paragraph = []
            fixed_lines.append(line)
        else:
            paragraph.append(stripped)
    # Add last paragraph if any
    if paragraph:
        fixed_lines.append(' '.join(paragraph) + '\n')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    print(f"Fixed file written to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_spaces.py <input_file.md>")
        sys.exit(1)
    fix_spaces(sys.argv[1])
