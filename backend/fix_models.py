import glob

files = glob.glob('/Users/siddharthpatni/.gemini/Cereforge/backend/app/models/*.py')
for f in files:
    with open(f, 'r') as file:
        lines = file.readlines()
    
    # Strip existing Optional imports that were misplaced
    cleaned_lines = []
    has_typing = False
    for line in lines:
        if line.strip() == 'from typing import Optional':
            pass
        else:
            if 'from typing import' in line:
                if 'Optional' not in line:
                    line = line.replace('from typing import ', 'from typing import Optional, ')
                has_typing = True
            cleaned_lines.append(line)
            
    content = "".join(cleaned_lines)
    
    if '| None' in content:
        content = content.replace('str | None', 'Optional[str]')
        content = content.replace('datetime | None', 'Optional[datetime]')
        content = content.replace('uuid.UUID | None', 'Optional[uuid.UUID]')
        content = content.replace('dict | None', 'Optional[dict]')
        
    if not has_typing and ('Optional' in content):
        # Insert Optional safely
        parts = content.split('from __future__ import annotations')
        if len(parts) > 1:
            content = parts[0] + 'from __future__ import annotations\nfrom typing import Optional\n' + parts[1].lstrip('\n')
        
    with open(f, 'w') as file:
        file.write(content)
