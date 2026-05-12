import os
import re

css_file = r'C:\Users\dangn\The Healthy Lab\foodie\assets\css\style.css'

with open(css_file, 'r', encoding='utf-8') as f:
    content = f.read()

sections = re.split(r'/\*-----------------------------------\*\\\n\s*#([A-Z\s]+)\n\\\*-----------------------------------\*/', content)

mq_content = ""
for i in range(1, len(sections), 2):
    if sections[i].strip() == "MEDIA QUERIES":
        mq_content = sections[i+1]
        break

# Find all @media blocks
media_blocks = re.split(r'(@media\s*\([^\{]+\)\s*\{)', mq_content)
# media_blocks[0] is whitespace/comments before the first @media
# media_blocks[1] is the @media signature
# media_blocks[2] is the content

print(f"Number of @media blocks: {len(media_blocks)//2}")
for i in range(1, len(media_blocks), 2):
    signature = media_blocks[i]
    content = media_blocks[i+1]
    
    # Inside the content, find sub-components
    sub_components = re.split(r'/\*\*\s*\n\s*\*\s*([A-Z\s]+)\n\s*\*/', content)
    print(f"Block: {signature.strip()} has {len(sub_components)//2} sub-components")
    for j in range(1, len(sub_components), 2):
        print(f"  - {sub_components[j]}")

