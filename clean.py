import re

def clean_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            # Remove all '#' characters
            line = line.replace('#', '')
            # Skip lines like <!-- Página N -->
            if re.match(r'<!-- Página \d+ -->', line.strip()):
                continue
            outfile.write(line)

# Usage
input_file = 'out_md/meditations_for_mortals_es.md'
output_file = 'out_md/meditations_for_mortals_es.cleaned.md'
clean_file(input_file, output_file)