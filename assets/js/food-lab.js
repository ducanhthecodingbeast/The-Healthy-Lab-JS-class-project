/**
 * FOOD LAB INTERACTIVE BUILDER LOGIC
 */

// Define the two formats
const FORMATS = {
  bowl: {
    id: 'bowl',
    name: 'Signature Bowl',
    basePrice: 9.99,
    steps: [
      { id: 'bases', title: '1. Choose Your Base', desc: 'Select up to 2', max: 2 },
      { id: 'proteins', title: '2. Pick a Protein', desc: 'Select 1', max: 1 },
      { id: 'accents', title: '3. Add Accents', desc: 'Select up to 4', max: 4 },
      { id: 'dressings', title: '4. Choose Dressing', desc: 'Select 1', max: 1 }
    ],
    ingredients: {
      bases: [
        { id: 'b1', name: 'Quinoa', cals: 220, pro: 8, carb: 39, fat: 3, price: 0, img: 'https://images.unsplash.com/photo-1586201375762-83865001e8ac?w=300&h=300&fit=crop' },
        { id: 'b2', name: 'Brown Rice', cals: 210, pro: 5, carb: 45, fat: 1, price: 0, img: 'https://images.unsplash.com/photo-1536215354-9721cb92eb82?w=300&h=300&fit=crop' },
        { id: 'b3', name: 'Baby Kale', cals: 35, pro: 3, carb: 6, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1576045057995-468b1a8d0774?w=300&h=300&fit=crop' },
        { id: 'b4', name: 'Edamame Mix', cals: 180, pro: 17, carb: 15, fat: 8, price: 1.50, img: 'https://images.unsplash.com/photo-1603513360682-10878e3532f1?w=300&h=300&fit=crop' }
      ],
      proteins: [
        { id: 'p1', name: 'Grilled Salmon', cals: 280, pro: 34, carb: 0, fat: 15, price: 5.00, img: 'https://images.unsplash.com/photo-1467003909585-2f8aa72700d6?w=300&h=300&fit=crop' },
        { id: 'p2', name: 'Herbed Chicken', cals: 210, pro: 38, carb: 2, fat: 5, price: 3.50, img: 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=300&h=300&fit=crop' },
        { id: 'p3', name: 'Smoked Tofu', cals: 160, pro: 16, carb: 4, fat: 9, price: 2.50, img: 'https://images.unsplash.com/photo-1583340578665-27a3dcb1c57e?w=300&h=300&fit=crop' },
        { id: 'p4', name: 'Crispy Falafel', cals: 320, pro: 12, carb: 30, fat: 18, price: 2.00, img: 'https://images.unsplash.com/photo-1595859714856-2db47bd8f8f9?w=300&h=300&fit=crop' }
      ],
      accents: [
        { id: 'a1', name: 'Avocado', cals: 160, pro: 2, carb: 9, fat: 15, price: 2.00, img: 'https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=300&h=300&fit=crop' },
        { id: 'a2', name: 'Hemp Seeds', cals: 55, pro: 3, carb: 1, fat: 4, price: 0.50, img: 'https://images.unsplash.com/photo-1590779083549-35491129bde5?w=300&h=300&fit=crop' },
        { id: 'a3', name: 'Pumpkin Seeds', cals: 85, pro: 4, carb: 2, fat: 7, price: 0.50, img: 'https://images.unsplash.com/photo-1590779083549-35491129bde5?w=300&h=300&fit=crop' },
        { id: 'a4', name: 'Sweet Potato', cals: 110, pro: 2, carb: 26, fat: 0, price: 1.00, img: 'https://images.unsplash.com/photo-1592688085458-1f6b5797371f?w=300&h=300&fit=crop' },
        { id: 'a5', name: 'Cherry Tomatoes', cals: 15, pro: 1, carb: 3, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1567306226416-b47dd793441a?w=300&h=300&fit=crop' },
        { id: 'a6', name: 'Pickled Onions', cals: 10, pro: 0, carb: 2, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1587049352847-495034c4f346?w=300&h=300&fit=crop' }
      ],
      dressings: [
        { id: 'd1', name: 'Lemon Tahini', cals: 120, pro: 3, carb: 5, fat: 10, price: 0, img: 'https://images.unsplash.com/photo-1472476443506-03c0042456e3?w=300&h=300&fit=crop' },
        { id: 'd2', name: 'Herb Vinaigrette', cals: 140, pro: 0, carb: 2, fat: 15, price: 0, img: 'https://images.unsplash.com/photo-1472476443506-03c0042456e3?w=300&h=300&fit=crop' },
        { id: 'd3', name: 'Miso Ginger', cals: 90, pro: 1, carb: 6, fat: 7, price: 0, img: 'https://images.unsplash.com/photo-1472476443506-03c0042456e3?w=300&h=300&fit=crop' },
        { id: 'd4', name: 'No Dressing', cals: 0, pro: 0, carb: 0, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1579361906297-c25bbdf642fc?w=300&h=300&fit=crop' }
      ]
    }
  },
  wrap: {
    id: 'wrap',
    name: 'Artisan Wrap',
    basePrice: 8.50,
    steps: [
      { id: 'wrapType', title: '1. Choose Wrap', desc: 'Select 1', max: 1 },
      { id: 'proteins', title: '2. Pick a Protein', desc: 'Select 1', max: 1 },
      { id: 'fillings', title: '3. Add Fillings', desc: 'Select up to 3', max: 3 },
      { id: 'sauce', title: '4. Choose Sauce', desc: 'Select 1', max: 1 }
    ],
    ingredients: {
      wrapType: [
        { id: 'w1', name: 'Spinach Tortilla', cals: 210, pro: 6, carb: 35, fat: 5, price: 0, img: 'https://images.unsplash.com/photo-1584947935041-0f62d16eb5a8?w=300&h=300&fit=crop' },
        { id: 'w2', name: 'Whole Wheat', cals: 190, pro: 5, carb: 32, fat: 4, price: 0, img: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300&h=300&fit=crop' },
        { id: 'w3', name: 'Gluten Free', cals: 230, pro: 3, carb: 40, fat: 6, price: 1.50, img: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=300&h=300&fit=crop' }
      ],
      proteins: [
        { id: 'p2', name: 'Herbed Chicken', cals: 210, pro: 38, carb: 2, fat: 5, price: 3.50, img: 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=300&h=300&fit=crop' },
        { id: 'p3', name: 'Smoked Tofu', cals: 160, pro: 16, carb: 4, fat: 9, price: 2.50, img: 'https://images.unsplash.com/photo-1583340578665-27a3dcb1c57e?w=300&h=300&fit=crop' },
        { id: 'p4', name: 'Crispy Falafel', cals: 320, pro: 12, carb: 30, fat: 18, price: 2.00, img: 'https://images.unsplash.com/photo-1595859714856-2db47bd8f8f9?w=300&h=300&fit=crop' },
        { id: 'p5', name: 'Spicy Tuna', cals: 190, pro: 28, carb: 0, fat: 8, price: 4.00, img: 'https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=300&h=300&fit=crop' }
      ],
      fillings: [
        { id: 'f1', name: 'Mixed Greens', cals: 15, pro: 1, carb: 3, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300&h=300&fit=crop' },
        { id: 'f2', name: 'Shredded Carrots', cals: 25, pro: 0, carb: 6, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=300&h=300&fit=crop' },
        { id: 'a1', name: 'Avocado', cals: 160, pro: 2, carb: 9, fat: 15, price: 2.00, img: 'https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=300&h=300&fit=crop' },
        { id: 'a6', name: 'Pickled Onions', cals: 10, pro: 0, carb: 2, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1587049352847-495034c4f346?w=300&h=300&fit=crop' }
      ],
      sauce: [
        { id: 's1', name: 'Garlic Aioli', cals: 150, pro: 1, carb: 2, fat: 16, price: 0, img: 'https://images.unsplash.com/photo-1551024601-bec78aea704b?w=300&h=300&fit=crop' },
        { id: 's2', name: 'Spicy Mayo', cals: 130, pro: 0, carb: 1, fat: 14, price: 0, img: 'https://images.unsplash.com/photo-1551024601-bec78aea704b?w=300&h=300&fit=crop' },
        { id: 'd1', name: 'Lemon Tahini', cals: 120, pro: 3, carb: 5, fat: 10, price: 0, img: 'https://images.unsplash.com/photo-1472476443506-03c0042456e3?w=300&h=300&fit=crop' }
      ]
    }
  },
  salad: {
    id: 'salad',
    name: 'Fresh Salad',
    basePrice: 8.99,
    steps: [
      { id: 'greens', title: '1. Choose Greens', desc: 'Select up to 2', max: 2 },
      { id: 'veggies', title: '2. Add Veggies', desc: 'Select up to 4', max: 4 },
      { id: 'proteins', title: '3. Pick a Protein', desc: 'Select 1', max: 1 },
      { id: 'dressings', title: '4. Choose Dressing', desc: 'Select 1', max: 1 }
    ],
    ingredients: {
      greens: [
        { id: 'g1', name: 'Baby Spinach', cals: 20, pro: 2, carb: 3, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1576045057995-468b1a8d0774?w=300&h=300&fit=crop' },
        { id: 'g2', name: 'Arugula', cals: 15, pro: 1, carb: 2, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300&h=300&fit=crop' },
        { id: 'g3', name: 'Mixed Greens', cals: 25, pro: 2, carb: 4, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300&h=300&fit=crop' },
        { id: 'g4', name: 'Romaine', cals: 15, pro: 1, carb: 3, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=300&h=300&fit=crop' }
      ],
      veggies: [
        { id: 'v1', name: 'Cucumber', cals: 10, pro: 0, carb: 2, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=300&h=300&fit=crop' },
        { id: 'v2', name: 'Cherry Tomatoes', cals: 15, pro: 1, carb: 3, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1567306226416-b47dd793441a?w=300&h=300&fit=crop' },
        { id: 'v3', name: 'Bell Peppers', cals: 20, pro: 1, carb: 4, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300&h=300&fit=crop' },
        { id: 'v4', name: 'Carrots', cals: 25, pro: 0, carb: 6, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=300&h=300&fit=crop' },
        { id: 'a1', name: 'Avocado', cals: 160, pro: 2, carb: 9, fat: 15, price: 2.00, img: 'https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=300&h=300&fit=crop' }
      ],
      proteins: [
        { id: 'p2', name: 'Herbed Chicken', cals: 210, pro: 38, carb: 2, fat: 5, price: 3.50, img: 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=300&h=300&fit=crop' },
        { id: 'p3', name: 'Smoked Tofu', cals: 160, pro: 16, carb: 4, fat: 9, price: 2.50, img: 'https://images.unsplash.com/photo-1583340578665-27a3dcb1c57e?w=300&h=300&fit=crop' },
        { id: 'p6', name: 'Boiled Egg', cals: 70, pro: 6, carb: 0, fat: 5, price: 1.00, img: 'https://images.unsplash.com/photo-1587486913049-53fc88980cfc?w=300&h=300&fit=crop' }
      ],
      dressings: [
        { id: 'd2', name: 'Herb Vinaigrette', cals: 140, pro: 0, carb: 2, fat: 15, price: 0, img: 'https://images.unsplash.com/photo-1472476443506-03c0042456e3?w=300&h=300&fit=crop' },
        { id: 'd5', name: 'Balsamic Glaze', cals: 90, pro: 0, carb: 22, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1472476443506-03c0042456e3?w=300&h=300&fit=crop' },
        { id: 'd6', name: 'Vegan Ranch', cals: 110, pro: 1, carb: 3, fat: 10, price: 0, img: 'https://images.unsplash.com/photo-1472476443506-03c0042456e3?w=300&h=300&fit=crop' }
      ]
    }
  },
  smoothie: {
    id: 'smoothie',
    name: 'Super Smoothie',
    basePrice: 6.99,
    steps: [
      { id: 'liquid', title: '1. Liquid Base', desc: 'Select 1', max: 1 },
      { id: 'fruits', title: '2. Fruits', desc: 'Select up to 3', max: 3 },
      { id: 'superfoods', title: '3. Superfoods', desc: 'Select up to 2', max: 2 }
    ],
    ingredients: {
      liquid: [
        { id: 'l1', name: 'Almond Milk', cals: 30, pro: 1, carb: 1, fat: 2, price: 0, img: 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=300&h=300&fit=crop' },
        { id: 'l2', name: 'Oat Milk', cals: 120, pro: 3, carb: 16, fat: 5, price: 0.50, img: 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=300&h=300&fit=crop' },
        { id: 'l3', name: 'Coconut Water', cals: 45, pro: 0, carb: 11, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=300&h=300&fit=crop' },
        { id: 'l4', name: 'Greek Yogurt', cals: 100, pro: 10, carb: 4, fat: 0, price: 1.00, img: 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=300&h=300&fit=crop' }
      ],
      fruits: [
        { id: 'fr1', name: 'Banana', cals: 105, pro: 1, carb: 27, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1481349518771-20055b2a7b24?w=300&h=300&fit=crop' },
        { id: 'fr2', name: 'Mixed Berries', cals: 70, pro: 1, carb: 15, fat: 0, price: 0.50, img: 'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=300&h=300&fit=crop' },
        { id: 'fr3', name: 'Mango', cals: 100, pro: 1, carb: 25, fat: 0, price: 0.50, img: 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=300&h=300&fit=crop' },
        { id: 'fr4', name: 'Pineapple', cals: 80, pro: 1, carb: 21, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1550258987-190a2d41a8ba?w=300&h=300&fit=crop' }
      ],
      superfoods: [
        { id: 'sf1', name: 'Chia Seeds', cals: 60, pro: 2, carb: 5, fat: 4, price: 0.50, img: 'https://images.unsplash.com/photo-1590779083549-35491129bde5?w=300&h=300&fit=crop' },
        { id: 'sf2', name: 'Protein Powder', cals: 120, pro: 25, carb: 2, fat: 1, price: 1.50, img: 'https://images.unsplash.com/photo-1579722820308-d74e571900a9?w=300&h=300&fit=crop' },
        { id: 'sf3', name: 'Maca Powder', cals: 20, pro: 1, carb: 4, fat: 0, price: 0.50, img: 'https://images.unsplash.com/photo-1579722820308-d74e571900a9?w=300&h=300&fit=crop' },
        { id: 'sf4', name: 'Spinach', cals: 10, pro: 1, carb: 1, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1576045057995-468b1a8d0774?w=300&h=300&fit=crop' }
      ]
    }
  },
  juice: {
    id: 'juice',
    name: 'Fresh Juice',
    basePrice: 5.99,
    steps: [
      { id: 'jbase', title: '1. Juice Base', desc: 'Select up to 2', max: 2 },
      { id: 'jboost', title: '2. Boosters', desc: 'Select up to 2', max: 2 }
    ],
    ingredients: {
      jbase: [
        { id: 'jb1', name: 'Apple', cals: 95, pro: 0, carb: 25, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1560806887-1e4cd0b6faa6?w=300&h=300&fit=crop' },
        { id: 'jb2', name: 'Orange', cals: 85, pro: 1, carb: 21, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1549888834-3ec93abae044?w=300&h=300&fit=crop' },
        { id: 'jb3', name: 'Carrot', cals: 50, pro: 1, carb: 12, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?w=300&h=300&fit=crop' },
        { id: 'jb4', name: 'Celery', cals: 15, pro: 0, carb: 3, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=300&h=300&fit=crop' }
      ],
      jboost: [
        { id: 'jbt1', name: 'Ginger', cals: 5, pro: 0, carb: 1, fat: 0, price: 0.50, img: 'https://images.unsplash.com/photo-1596368708356-6e1e1025ee72?w=300&h=300&fit=crop' },
        { id: 'jbt2', name: 'Turmeric', cals: 5, pro: 0, carb: 1, fat: 0, price: 0.50, img: 'https://images.unsplash.com/photo-1615486171448-4df1712a4df4?w=300&h=300&fit=crop' },
        { id: 'jbt3', name: 'Lemon', cals: 10, pro: 0, carb: 3, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1587313632739-c895b98cb9bd?w=300&h=300&fit=crop' },
        { id: 'jbt4', name: 'Mint', cals: 5, pro: 0, carb: 1, fat: 0, price: 0, img: 'https://images.unsplash.com/photo-1620215714364-58273646ce66?w=300&h=300&fit=crop' }
      ]
    }
  }
};

let currentFormatId = 'bowl';
let state = {};
let cart = [];

// DOM Elements
const builderSteps = document.getElementById('builder-steps');
const valCal = document.getElementById('val-cal');
const valPro = document.getElementById('val-pro');
const valCarb = document.getElementById('val-carb');
const valFat = document.getElementById('val-fat');
const valPrice = document.getElementById('val-price');
const compositionList = document.getElementById('composition-list');
const checkoutBtn = document.querySelector('.checkout-btn');

// Cart DOM
const cartBtn = document.getElementById('cart-btn');
const cartBadge = document.getElementById('cart-badge');
const cartModal = document.getElementById('cart-modal');
const closeCartBtn = document.getElementById('close-cart');
const cartItemsContainer = document.getElementById('cart-items');
const cartTotalPrice = document.getElementById('cart-total-price');

function init() {
  renderFormatSelector();
  setFormat('bowl');

  // "Add to Cart" button (the builder's main CTA)
  checkoutBtn.addEventListener('click', addToCart);

  // Cart UI is handled by the shared cart.js
}

function renderFormatSelector() {
  const formatDiv = document.createElement('div');
  formatDiv.className = 'format-selector';
  
  formatDiv.innerHTML = `
    <button class="format-btn active" id="btn-format-bowl" onclick="setFormat('bowl')">Signature Bowl</button>
    <button class="format-btn" id="btn-format-wrap" onclick="setFormat('wrap')">Artisan Wrap</button>
    <button class="format-btn" id="btn-format-salad" onclick="setFormat('salad')">Fresh Salad</button>
    <button class="format-btn" id="btn-format-smoothie" onclick="setFormat('smoothie')">Smoothies</button>
    <button class="format-btn" id="btn-format-juice" onclick="setFormat('juice')">Fresh Juices</button>
  `;
  
  // Insert before builder steps
  builderSteps.parentNode.insertBefore(formatDiv, builderSteps);
}

function setFormat(formatId) {
  currentFormatId = formatId;
  const format = FORMATS[formatId];
  
  // Update Buttons UI
  document.querySelectorAll('.format-btn').forEach(btn => btn.classList.remove('active'));
  document.getElementById(`btn-format-${formatId}`).classList.add('active');

  // Reset State
  state = {};
  format.steps.forEach(step => {
    state[step.id] = [];
  });

  renderSteps();
  updateNutrition();
}

function renderSteps() {
  builderSteps.innerHTML = '';
  const format = FORMATS[currentFormatId];
  
  format.steps.forEach(step => {
    const items = format.ingredients[step.id];
    builderSteps.appendChild(createStep(step.title, step.desc, items, step.id, step.max));
  });
}

function createStep(titleText, descText, items, category, maxSelect) {
  const stepDiv = document.createElement('div');
  stepDiv.className = 'step-group';

  const title = document.createElement('h3');
  title.className = 'step-title';
  title.innerHTML = `<span>${titleText}</span> <span style="font-size: 1.4rem; font-weight: 400; color: var(--text-muted);">${descText}</span>`;
  stepDiv.appendChild(title);

  const grid = document.createElement('div');
  grid.className = 'ingredient-grid';

  items.forEach(item => {
    const card = document.createElement('div');
    card.className = `ingredient-card ${state[category].includes(item.id) ? 'selected' : ''}`;
    card.onclick = () => handleSelect(category, item.id, maxSelect);

    const priceHtml = item.price > 0 ? `<div class="ingredient-price">+$${item.price.toFixed(2)}</div>` : '';

    card.innerHTML = `
      <div class="ingredient-name">${item.name}</div>
      <div class="ingredient-cals">${item.cals} cal</div>
      ${priceHtml}
    `;
    grid.appendChild(card);
  });

  stepDiv.appendChild(grid);
  return stepDiv;
}

function handleSelect(category, id, maxSelect) {
  const selectedList = state[category];
  
  if (selectedList.includes(id)) {
    // Deselect
    state[category] = selectedList.filter(itemId => itemId !== id);
  } else {
    // Select
    if (selectedList.length >= maxSelect) {
      if (maxSelect === 1) {
        state[category] = [id]; // replace
      } else {
        return; // do nothing if max
      }
    } else {
      state[category].push(id);
    }
  }

  renderSteps();
  updateNutrition();
}

function updateNutrition() {
  const format = FORMATS[currentFormatId];
  let totals = { cals: 0, pro: 0, carb: 0, fat: 0, price: format.basePrice };
  let selectedItems = [];

  format.steps.forEach(step => {
    const cat = step.id;
    state[cat].forEach(id => {
      const item = format.ingredients[cat].find(i => i.id === id);
      if (item) {
        totals.cals += item.cals;
        totals.pro += item.pro;
        totals.carb += item.carb;
        totals.fat += item.fat;
        totals.price += item.price;
        selectedItems.push(item);
      }
    });
  });

  // Update DOM numbers
  valCal.innerText = totals.cals;
  valPro.innerText = totals.pro + 'g';
  valCarb.innerText = totals.carb + 'g';
  valFat.innerText = totals.fat + 'g';
  valPrice.innerText = '$' + totals.price.toFixed(2);

  // Update composition list
  if (selectedItems.length === 0) {
    compositionList.innerHTML = '<li class="empty-msg">Start selecting ingredients...</li>';
  } else {
    compositionList.innerHTML = '';
    selectedItems.forEach(item => {
      const li = document.createElement('li');
      li.className = 'composition-item';
      li.innerHTML = `
        <span class="item-name">${item.name}</span>
        <span class="item-cals">${item.cals} cal</span>
      `;
      compositionList.appendChild(li);
    });
  }
}

// CART LOGIC
function addToCart() {
  const format = FORMATS[currentFormatId];
  
  // Validate if they selected required items
  let isValid = true;
  if(currentFormatId === 'bowl' && state.bases.length === 0) isValid = false;
  if(currentFormatId === 'wrap' && state.wrapType.length === 0) isValid = false;
  if(currentFormatId === 'salad' && state.greens.length === 0) isValid = false;
  if(currentFormatId === 'smoothie' && state.liquid.length === 0) isValid = false;
  if(currentFormatId === 'juice' && state.jbase.length === 0) isValid = false;
  
  if(!isValid) {
    showToast('Please select a base first!', 'warning-outline');
    return;
  }

  let selectedItems = [];
  let itemTotal = format.basePrice;

  format.steps.forEach(step => {
    state[step.id].forEach(id => {
      const item = format.ingredients[step.id].find(i => i.id === id);
      if (item) {
        selectedItems.push(item.name);
        itemTotal += item.price;
      }
    });
  });

  const cartItem = {
    id: Date.now(),
    name: format.name,
    category: currentFormatId,
    details: selectedItems.join(', '),
    price: itemTotal
  };

  // Use the shared Cart system (persists to localStorage)
  if (typeof Cart !== 'undefined') {
    Cart.add(cartItem);
  }

  // Reset format
  setFormat(currentFormatId);
}

function updateCartUI() {
  // Delegate to shared Cart system
  if (typeof Cart !== 'undefined') {
    Cart.renderBadge();
    Cart.renderDrawer();
  }
}

function showToast(msg, icon) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<ion-icon name="${icon}"></ion-icon> ${msg}`;
  
  container.appendChild(toast);

  // Remove after 3s
  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease forwards';
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', init);
