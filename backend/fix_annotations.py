import os
import glob

files = glob.glob('/Users/siddharthpatni/.gemini/Cereforge/backend/app/**/*.py', recursive=True)
files += glob.glob('/Users/siddharthpatni/.gemini/Cereforge/backend/tests/**/*.py', recursive=True)
files = [f for f in files if '/venv/' not in f]

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    if 'from __future__ import annotations' not in content:
        if content.startswith('"""'):
            parts = content.split('"""', 2)
            if len(parts) >= 3:
                content = parts[0] + '"""' + parts[1] + '"""\n\nfrom __future__ import annotations\n' + parts[2]
        else:
            content = 'from __future__ import annotations\n\n' + content
            
        with open(f, 'w') as file:
            file.write(content)
        print("Patched:", f)
