const fs = require('fs');
const path = require('path');

const jsPath = path.join(__dirname, '../assets/js/food-lab.js');
let content = fs.readFileSync(jsPath, 'utf8');

const imageMap = {
  'Quinoa': 'https://images.unsplash.com/photo-1586201375762-83865001e8ac?w=300&h=300&fit=crop',
  'Brown Rice': 'https://images.unsplash.com/photo-1536215354-9721cb92eb82?w=300&h=300&fit=crop',
  'Baby Kale': 'https://images.unsplash.com/photo-1576045057995-468b1a8d0774?w=300&h=300&fit=crop',
  'Edamame Mix': 'https://images.unsplash.com/photo-1603513360682-10878e3532f1?w=300&h=300&fit=crop',
  'Grilled Salmon': 'https://images.unsplash.com/photo-1467003909585-2f8aa72700d6?w=300&h=300&fit=crop',
  'Herbed Chicken': 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=300&h=300&fit=crop',
  'Smoked Tofu': 'https://images.unsplash.com/photo-1583340578665-27a3dcb1c57e?w=300&h=300&fit=crop',
  'Crispy Falafel': 'https://images.unsplash.com/photo-1595859714856-2db47bd8f8f9?w=300&h=300&fit=crop',
  'Avocado': 'https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=300&h=300&fit=crop',
  'Hemp Seeds': 'https://images.unsplash.com/photo-1590779083549-35491129bde5?w=300&h=300&fit=crop',
  'Pumpkin Seeds': 'https://images.unsplash.com/photo-1590779083549-35491129bde5?w=300&h=300&fit=crop',
  'Sweet Potato': 'https://images.unsplash.com/photo-1592688085458-1f6b5797371f?w=300&h=300&fit=crop',
  'Cherry Tomatoes': 'https://images.unsplash.com/photo-1567306226416-b47dd793441a?w=300&h=300&fit=crop',
  'Pickled Onions': 'https://images.unsplash.com/photo-1587049352847-495034c4f346?w=300&h=300&fit=crop',
  'Lemon Tahini': 'https://images.unsplash.com/photo-1472476443506-03c0042456e3?w=300&h=300&fit=crop',
  'Herb Vinaigrette': 'https://images.unsplash.com/photo-1472476443506-03c0042456e3?w=300&h=300&fit=crop',
  'Miso Ginger': 'https://images.unsplash.com/photo-1472476443506-03c0042456e3?w=300&h=300&fit=crop',
  'No Dressing': 'https://images.unsplash.com/photo-1579361906297-c25bbdf642fc?w=300&h=300&fit=crop',
  'Spinach Tortilla': 'https://images.unsplash.com/photo-1584947935041-0f62d16eb5a8?w=300&h=300&fit=crop',
  'Whole Wheat': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300&h=300&fit=crop',
  'Gluten Free': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300&h=300&fit=crop',
  'Spicy Tuna': 'https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=300&h=300&fit=crop',
  'Mixed Greens': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300&h=300&fit=crop',
  'Shredded Carrots': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=300&h=300&fit=crop',
  'Garlic Aioli': 'https://images.unsplash.com/photo-1551024601-bec78aea704b?w=300&h=300&fit=crop',
  'Spicy Mayo': 'https://images.unsplash.com/photo-1551024601-bec78aea704b?w=300&h=300&fit=crop',
  'Baby Spinach': 'https://images.unsplash.com/photo-1576045057995-468b1a8d0774?w=300&h=300&fit=crop',
  'Arugula': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300&h=300&fit=crop',
  'Romaine': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300&h=300&fit=crop',
  'Cucumber': 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=300&h=300&fit=crop', // placeholder
  'Bell Peppers': 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300&h=300&fit=crop',
  'Carrots': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=300&h=300&fit=crop',
  'Boiled Egg': 'https://images.unsplash.com/photo-1587486913049-53fc88980cfc?w=300&h=300&fit=crop',
  'Balsamic Glaze': 'https://images.unsplash.com/photo-1472476443506-03c0042456e3?w=300&h=300&fit=crop',
  'Vegan Ranch': 'https://images.unsplash.com/photo-1472476443506-03c0042456e3?w=300&h=300&fit=crop',
  'Almond Milk': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=300&h=300&fit=crop',
  'Oat Milk': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=300&h=300&fit=crop',
  'Coconut Water': 'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=300&h=300&fit=crop',
  'Greek Yogurt': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=300&h=300&fit=crop',
  'Banana': 'https://images.unsplash.com/photo-1481349518771-20055b2a7b24?w=300&h=300&fit=crop',
  'Mixed Berries': 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=300&h=300&fit=crop',
  'Mango': 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=300&h=300&fit=crop',
  'Pineapple': 'https://images.unsplash.com/photo-1550258987-190a2d41a8ba?w=300&h=300&fit=crop',
  'Chia Seeds': 'https://images.unsplash.com/photo-1590779083549-35491129bde5?w=300&h=300&fit=crop',
  'Protein Powder': 'https://images.unsplash.com/photo-1579722820308-d74e571900a9?w=300&h=300&fit=crop',
  'Maca Powder': 'https://images.unsplash.com/photo-1579722820308-d74e571900a9?w=300&h=300&fit=crop',
  'Spinach': 'https://images.unsplash.com/photo-1576045057995-468b1a8d0774?w=300&h=300&fit=crop',
  'Apple': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6faa6?w=300&h=300&fit=crop',
  'Orange': 'https://images.unsplash.com/photo-1549888834-3ec93abae044?w=300&h=300&fit=crop',
  'Carrot': 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=300&h=300&fit=crop',
  'Celery': 'https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=300&h=300&fit=crop',
  'Ginger': 'https://images.unsplash.com/photo-1596368708356-6e1e1025ee72?w=300&h=300&fit=crop',
  'Turmeric': 'https://images.unsplash.com/photo-1615486171448-4df1712a4df4?w=300&h=300&fit=crop',
  'Lemon': 'https://images.unsplash.com/photo-1587313632739-c895b98cb9bd?w=300&h=300&fit=crop',
  'Mint': 'https://images.unsplash.com/photo-1620215714364-58273646ce66?w=300&h=300&fit=crop'
};

const regex = /{ id:\s*'[^']+',\s*name:\s*'([^']+)'([^}]*?)(?:,\s*img:\s*'[^']*')?\s*}/g;
let newContent = content.replace(regex, (match, name, rest) => {
  const imgUrl = imageMap[name] || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=300&h=300&fit=crop';
  return `{ id: '${match.match(/id:\s*'([^']+)'/)[1]}', name: '${name}'${rest}, img: '${imgUrl}' }`;
});

// Update the createStep function block
const oldCardHtml = `    card.innerHTML = \`
      <div class="ingredient-name">\${item.name}</div>
      <div class="ingredient-cals">\${item.cals} cal</div>
      \${priceHtml}
    \`;`;

const newCardHtml = `    card.innerHTML = \`
      <div class="card-img-wrapper">
        <img src="\${item.img}" alt="\${item.name}" class="ingredient-img" loading="lazy">
        <div class="selected-badge"><ion-icon name="checkmark-circle"></ion-icon></div>
      </div>
      <div class="card-content">
        <div class="ingredient-name">\${item.name}</div>
        <div class="ingredient-cals">\${item.cals} cal</div>
        \${priceHtml}
      </div>
    \`;`;

newContent = newContent.replace(oldCardHtml, newCardHtml);

fs.writeFileSync(jsPath, newContent, 'utf8');
console.log('Successfully updated food-lab.js with images and new card HTML.');
