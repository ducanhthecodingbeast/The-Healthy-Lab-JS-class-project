import os
import re
from collections import defaultdict

css_file = r'C:\Users\dangn\The Healthy Lab\foodie\assets\css\style.css'

with open(css_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Split by top-level section headers
sections = re.split(r'/\*-----------------------------------\*\\\n\s*#([A-Z\s]+)\n\\\*-----------------------------------\*/', content)

print(f"Number of sections found: {len(sections)//2}")
for i in range(1, len(sections), 2):
    print(f"Found section: {sections[i].strip()}")

