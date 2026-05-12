import os
import re
from collections import defaultdict

css_file = r'C:\Users\dangn\The Healthy Lab\foodie\assets\css\style.css'
out_dir = r'C:\Users\dangn\The Healthy Lab\foodie\assets\css'

with open(css_file, 'r', encoding='utf-8') as f:
    css = f.read()

file_mapping = {
    'CUSTOM PROPERTY': 'golden-harvest.css',
    'RESET': 'golden-harvest.css',
    'REUSED STYLE': 'golden-harvest.css',
    'BACK TO TOP': 'golden-harvest.css',
    'HEADER': 'nav.css',
    'SEARCH BOX': 'nav.css',
    'HERO': 'hero.css',
    'PROMO': 'about.css',
    'ABOUT': 'about.css',
    'FOOD MENU': 'menu.css',
    'CTA': 'delivery.css',
    'DELIVERY': 'delivery.css',
    'TESTIMONIALS': 'testimonials.css',
    'BANNER': 'foodie-banner.css',
    'BLOG': 'blog.css',
    'FOOTER': 'skip',
}

output_files = defaultdict(str)

sections = re.split(r'/\*-----------------------------------\*\\\n\s*#([A-Z\s]+)\n\\\*-----------------------------------\*/', css)
output_files['golden-harvest.css'] += sections[0].strip() + "\n\n"

for i in range(1, len(sections), 2):
    name = sections[i].strip()
    if name == 'MEDIA QUERIES' or "THE HEALTHY LAB" in name:
        continue
    
    filename = file_mapping.get(name, 'golden-harvest.css')
    if filename != 'skip':
        output_files[filename] += f"/*-----------------------------------*\\\n  #{name}\n\\*-----------------------------------*/\n"
        output_files[filename] += sections[i+1].strip() + "\n\n"

for i in range(1, len(sections), 2):
    if "THE HEALTHY LAB" in sections[i].strip():
        output_files['foodie-banner.css'] += f"/*-----------------------------------*\\\n  #CUSTOM ADDITIONS\n\\*-----------------------------------*/\n"
        output_files['foodie-banner.css'] += sections[i+1].strip() + "\n\n"

mq_block = ""
for i in range(1, len(sections), 2):
    if sections[i].strip() == 'MEDIA QUERIES':
        mq_block = sections[i+1]
        break

def parse_media_queries(mq_text):
    idx = 0
    while True:
        m = re.search(r'@media\s*\([^{]+\)\s*\{', mq_text[idx:])
        if not m:
            break
        start = idx + m.start()
        sig = m.group(0)
        
        brace_count = 1
        pos = idx + m.end()
        while brace_count > 0 and pos < len(mq_text):
            if mq_text[pos] == '{':
                brace_count += 1
            elif mq_text[pos] == '}':
                brace_count -= 1
            pos += 1
            
        full_mq = mq_text[start:pos]
        idx = pos
        
        inner_content = full_mq[len(sig):-1]
        
        sub_sections = re.split(r'/\*\*\s*\n\s*\*\s*([A-Z\s]+)\n\s*\*/', inner_content)
        
        for j in range(1, len(sub_sections), 2):
            sub_name = sub_sections[j].strip()
            sub_css = sub_sections[j+1].strip()
            
            filename = file_mapping.get(sub_name, 'golden-harvest.css')
            if filename != 'skip' and sub_css:
                output_files[filename] += f"{sig}\n  /**\n   * {sub_name}\n   */\n  {sub_css}\n}}\n\n"

parse_media_queries(mq_block)

for filename, content in output_files.items():
    if filename != 'skip':
        with open(os.path.join(out_dir, filename), 'w', encoding='utf-8') as f:
            f.write(content)

print("Split completed successfully!")
