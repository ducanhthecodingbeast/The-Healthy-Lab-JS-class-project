import re

with open('food-lab-wrap.html', 'r') as f:
    content = f.read()

images = [
    "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300&h=300&fit=crop", # Whole wheat
    "https://images.unsplash.com/photo-1584947935041-0f62d16eb5a8?w=300&h=300&fit=crop", # Spinach
    "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300&h=300&fit=crop", # Gluten free
    "https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=300&h=300&fit=crop", # Halloumi
    "https://images.unsplash.com/photo-1574672280600-4accfa5b6f98?w=300&h=300&fit=crop", # Turkey
    "https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=300&h=300&fit=crop", # Chickpeas
    "https://images.unsplash.com/photo-1577002820352-78d104278fc0?w=300&h=300&fit=crop", # Hummus
    "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300&h=300&fit=crop", # Peppers
    "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300&h=300&fit=crop", # Arugula
    "https://images.unsplash.com/photo-1551024601-bec78aea704b?w=300&h=300&fit=crop", # Tzatziki
    "https://images.unsplash.com/photo-1587049352847-495034c4f346?w=300&h=300&fit=crop", # Pickled onions
    "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=300&h=300&fit=crop", # Avocado
]

placeholder = 'src="https://www.gstatic.com/labs-code/stitch/stitch-placeholder-300x300.svg"'

for img_url in images:
    content = content.replace(placeholder, f'src="{img_url}"', 1)

with open('food-lab-wrap.html', 'w') as f:
    f.write(content)

print("Replaced images.")
