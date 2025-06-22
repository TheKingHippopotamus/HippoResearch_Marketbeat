import os
import shutil

ARTICLES_DIR = 'articles'

for fname in os.listdir(ARTICLES_DIR):
    if fname.endswith('.html') and not fname.endswith('.bak'):
        bak_path = os.path.join(ARTICLES_DIR, fname + '.bak')
        orig_path = os.path.join(ARTICLES_DIR, fname)
        if os.path.exists(bak_path):
            shutil.copy2(bak_path, orig_path)
            print(f'שוחזר: {fname}')
        else:
            print(f'אין גיבוי עבור: {fname}')
print('שחזור הושלם!') 