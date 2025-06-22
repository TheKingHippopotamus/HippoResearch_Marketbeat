import os
import re
import glob

TEMPLATE_PATH = 'article_template.html'
ARTICLES_DIR = 'articles'
BACKUP_EXT = '.bak'

def extract_media_blocks(text):
    lines = text.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith('@media (max-width: 768px) {'):
            block = [lines[i]]
            brace_count = lines[i].count('{') - lines[i].count('}')
            i += 1
            while i < len(lines) and brace_count > 0:
                block.append(lines[i])
                brace_count += lines[i].count('{') - lines[i].count('}')
                i += 1
            blocks.append('\n'.join(block))
        else:
            i += 1
    return blocks

with open(TEMPLATE_PATH, encoding='utf-8') as f:
    template = f.read()

media_blocks = extract_media_blocks(template)
if not media_blocks:
    print('DEBUG: No @media blocks found with block parser.')
    for i, line in enumerate(template.splitlines()):
        if '@media' in line:
            print(f'Line {i+1}: {line}')
    raise RuntimeError('No @media (max-width: 768px) block found in template!')
new_media_css = '\n'.join(media_blocks)

# Regex to remove all @media (max-width: 768px) blocks (even if nested)
remove_pattern = re.compile(r'@media \(max-width: 768px\) \{[\s\S]+?^\}', re.MULTILINE)

html_files = glob.glob(os.path.join(ARTICLES_DIR, '*.html'))
updated = []
for path in html_files:
    with open(path, encoding='utf-8') as f:
        content = f.read()
    if '@media (max-width: 768px)' in content:
        bak_path = path + BACKUP_EXT
        with open(bak_path, 'w', encoding='utf-8') as f:
            f.write(content)
        new_content = remove_pattern.sub('', content)
        new_content = re.sub(r'(</style>)', f'{new_media_css}\n\\1', new_content, count=1)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        updated.append(os.path.basename(path))

print(f'Updated {len(updated)} files:')
for fname in updated:
    print('  -', fname)
if not updated:
    print('No files were updated (no @media block found in any file).') 