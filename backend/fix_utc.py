import os
import glob

files = glob.glob('/Users/siddharthpatni/.gemini/Cereforge/backend/app/**/*.py', recursive=True)

for f in files:
    with open(f, 'r') as file:
        content = file.read()
    
    original = content
    content = content.replace('from datetime import UTC, datetime, timedelta', 'from datetime import datetime, timedelta, timezone')
    content = content.replace('from datetime import UTC, datetime', 'from datetime import datetime, timezone')
    content = content.replace('from datetime import UTC', 'from datetime import timezone')
    content = content.replace('datetime.now(UTC)', 'datetime.now(timezone.utc)')
    
    if content != original:
        with open(f, 'w') as file:
            file.write(content)
        print(f"Updated {f}")
