import os
import shutil
import glob

ARTICLES_DIR = 'articles'

glob_path = 'articles/*.html.bak'
restored = []
for bak_path in glob.glob(glob_path):
    html_path = bak_path[:-4]  # remove .bak
    with open(bak_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    restored.append(os.path.basename(html_path))
print(f'Restored {len(restored)} files:')
for fname in restored:
    print('  -', fname)
if not restored:
    print('No files restored.')

print('שחזור הושלם!') 