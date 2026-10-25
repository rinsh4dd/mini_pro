import os
import re

print("=== CHECKING myapp/views.py FOR EMAIL VALIDATION ===")
with open('myapp/views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

lines = views_content.splitlines()
for i, l in enumerate(lines):
    if re.search(r'email', l, re.IGNORECASE) and any(k in l for k in ['regex', 'match', 'POST', 'filter', 'error', 'warning', 'messages']):
        print(f"views.py:{i+1}: {l.strip()}")

print("\n=== CHECKING TEMPLATES FOR EMAIL INPUTS ===")
template_dir = 'templates'
for root, dirs, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                t_lines = content.splitlines()
                for idx, tl in enumerate(t_lines):
                    if 'type="email"' in tl or 'name="email"' in tl or "name='email'" in tl or 'id="email"' in tl:
                        print(f"{filepath}:{idx+1}: {tl.strip()[:110]}")
