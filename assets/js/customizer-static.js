document.addEventListener('DOMContentLoaded', () => {
  // --- 1. SETUP TAB NAVIGATION ---
  const tabLinks = document.querySelectorAll('[data-purpose="category-navigation"] button, nav a, nav button');
  tabLinks.forEach(tab => {
    const text = tab.innerText.toLowerCase();
    tab.style.cursor = 'pointer';
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      if (text.includes('bowl')) window.location.href = 'food-lab.html';
      else if (text.includes('salad')) window.location.href = 'food-lab-salad.html';
      else if (text.includes('wrap')) window.location.href = 'food-lab-wrap.html';
      else if (text.includes('smoothie')) window.location.href = 'food-lab-smoothie.html';
      else if (text.includes('juice')) window.location.href = 'food-lab-juice.html';
    });
  });

  // --- 2. MACROS & PRICING DATABASE ---
  // A rough dictionary of protein, carbs, fats (since they aren't in the HTML).
  // Calories and Price will be parsed directly from the HTML to match the visuals!
  const MACROS = {
    'Quinoa': { p: 8, c: 39, f: 3 }, 'Brown Rice': { p: 5, c: 45, f: 1 }, 'Baby Kale': { p: 3, c: 6, f: 0 }, 'Edamame Mix': { p: 17, c: 15, f: 8 },
    'Grilled Salmon': { p: 34, c: 0, f: 15 }, 'Herbed Chicken': { p: 38, c: 2, f: 5 }, 'Smoked Tofu': { p: 16, c: 4, f: 9 }, 'Crispy Falafel': { p: 12, c: 30, f: 18 },
    'Avocado': { p: 2, c: 9, f: 15 }, 'Hemp Seeds': { p: 3, c: 1, f: 4 }, 'Pumpkin Seeds': { p: 4, c: 2, f: 7 }, 'Sweet Potato': { p: 2, c: 26, f: 0 },
    'Cherry Tomatoes': { p: 1, c: 3, f: 0 }, 'Pickled Onions': { p: 0, c: 2, f: 0 },
    'Mixed Field Greens': { p: 1, c: 2, f: 0 }, 'Baby Spinach': { p: 2, c: 3, f: 0 }, 'Romaine': { p: 1, c: 3, f: 0 },
    'Poached Egg': { p: 6, c: 0, f: 5 }, 'Grilled Steak Strips': { p: 25, c: 0, f: 10 }, 'Tempeh': { p: 15, c: 9, f: 4 },
    'Sunflower Seeds': { p: 6, c: 6, f: 14 }, 'Lemon Tahini': { p: 3, c: 5, f: 10 }, 'Balsamic Glaze': { p: 0, c: 15, f: 0 },
    'Whole Wheat Wrap': { p: 5, c: 32, f: 4 }, 'Spinach Wrap': { p: 6, c: 35, f: 5 }, 'Gluten-Free Teff Wrap': { p: 3, c: 40, f: 6 },
    'Grilled Halloumi': { p: 15, c: 2, f: 18 }, 'Roasted Turkey': { p: 28, c: 0, f: 2 }, 'Spicy Chickpeas': { p: 8, c: 25, f: 4 },
    'Hummus': { p: 4, c: 9, f: 5 }, 'Roasted Peppers': { p: 1, c: 5, f: 0 }, 'Arugula': { p: 1, c: 2, f: 0 }, 'Tzatziki': { p: 3, c: 4, f: 5 },
    'Almond Milk': { p: 1, c: 1, f: 2 }, 'Coconut Water': { p: 0, c: 11, f: 0 }, 'Cold-Pressed Apple Juice': { p: 0, c: 28, f: 0 },
    'Dragonfruit': { p: 2, c: 15, f: 0 }, 'Kale': { p: 3, c: 6, f: 0 }, 'Ginger': { p: 0, c: 1, f: 0 },
    'Chia Seeds': { p: 2, c: 5, f: 4 }, 'Ashwagandha': { p: 0, c: 2, f: 0 }, 'Spirulina': { p: 4, c: 1, f: 0 },
    'Carrot Juice': { p: 1, c: 22, f: 0 }, 'Celery Juice': { p: 1, c: 9, f: 0 }, 'Cold-Pressed Apple': { p: 0, c: 28, f: 0 },
    'Lemon': { p: 0, c: 3, f: 0 }, 'Turmeric': { p: 0, c: 2, f: 0 }, 'Mint': { p: 0, c: 1, f: 0 },
    'Wheatgrass Shot': { p: 2, c: 2, f: 0 }, 'Activated Charcoal': { p: 0, c: 0, f: 0 }, 'Aloe Vera': { p: 0, c: 3, f: 0 }
  };

  const getFormatBasePrice = () => {
    if (window.location.pathname.includes('salad')) return 8.99;
    if (window.location.pathname.includes('wrap')) return 8.50;
    if (window.location.pathname.includes('smoothie')) return 6.99;
    if (window.location.pathname.includes('juice')) return 5.99;
    return 9.99; // Bowl base
  };

  let selectedItems = [];

  // --- 3. PARSE CARDS AND MAKE INTERACTIVE ---
  // We identify cards as divs inside the grid that are meant to be selectable
  const cards = document.querySelectorAll('main .grid > div, main .selectable-group > div');
  
  cards.forEach(card => {
    // Ensure it's a selectable card
    if (!card.className.includes('cursor-pointer') && !card.className.includes('item-card') && !card.className.includes('topping-card')) {
      card.style.cursor = 'pointer';
    }

    // Parse Name, Calories, Price from DOM
    const texts = Array.from(card.querySelectorAll('p, span')).filter(el => el.children.length === 0);
    if (texts.length < 2) return;

    const name = texts[0].innerText.trim();
    const subtext = texts[1].innerText.trim().toLowerCase(); 
    
    const calMatch = subtext.match(/(\d+)\s*cal/);
    const priceMatch = subtext.match(/\+\$([\d\.]+)/);
    
    const cals = calMatch ? parseInt(calMatch[1]) : 0;
    const price = priceMatch ? parseFloat(priceMatch[1]) : 0;
    
    const macros = MACROS[name] || { p: 0, c: 0, f: 0 };
    
    // Attach click handler
    card.addEventListener('click', () => {
      // Toggle Selection
      const isSelected = selectedItems.find(i => i.name === name);
      
      // Look up max selections for this section
      const section = card.closest('section, [data-purpose^="step-"], .mb-12');
      const sectionTitle = section ? section.querySelector('h2, h3') : null;
      let maxAllowed = 99;
      if (sectionTitle) {
        const titleText = sectionTitle.innerText;
        const maxMatch = titleText.match(/Select\s*(?:up\s*to\s*)?(\d+)/i);
        if (maxMatch) maxAllowed = parseInt(maxMatch[1]);
      }
      
      const itemsInSection = selectedItems.filter(i => i.section === section);
      
      if (isSelected) {
        // Deselect
        selectedItems = selectedItems.filter(i => i.name !== name);
        removeSelectedStyling(card);
      } else {
        // Select
        if (itemsInSection.length >= maxAllowed) {
          // Deselect the oldest one in this section to allow the new one
          const oldest = itemsInSection[0];
          selectedItems = selectedItems.filter(i => i.name !== oldest.name);
          removeSelectedStyling(oldest.card);
        }
        selectedItems.push({ name, cals, price, p: macros.p, c: macros.c, f: macros.f, section, card });
        addSelectedStyling(card);
      }
      
      updateSidebar();
    });
  });
  
  function addSelectedStyling(card) {
    card.classList.add('selected');
  }
  
  function removeSelectedStyling(card) {
    card.classList.remove('selected');
  }

  // --- 4. UPDATE SIDEBAR ---
  function updateSidebar() {
    let tCals = 0, tPro = 0, tCarb = 0, tFat = 0, tPrice = getFormatBasePrice();
    const names = [];
    
    selectedItems.forEach(item => {
      tCals += item.cals;
      tPro += item.p;
      tCarb += item.c;
      tFat += item.f;
      tPrice += item.price;
      names.push(item.name);
    });
    
    // Find sidebar elements
    const setVal = (label, val) => {
      const els = Array.from(document.querySelectorAll('*')).filter(el => el.textContent.trim().toUpperCase() === label.toUpperCase() && el.children.length === 0);
      if (els.length > 0) {
        // Usually the value is in a <p> or <div> right before the label, or first child of parent
        const parent = els[els.length - 1].parentElement;
        const valEl = parent.querySelector('p:first-child, div:first-child');
        if (valEl && valEl !== els[els.length - 1]) {
          valEl.innerText = val;
        }
      }
    };
    
    setVal('CALORIES', tCals);
    setVal('PROTEIN', `${tPro}g`);
    setVal('CARBS', `${tCarb}g`);
    setVal('FATS', `${tFat}g`);
    
    // Price
    const priceEl = document.querySelector('[data-purpose="pricing"] span:last-child') || document.querySelector('#val-price');
    if (priceEl) {
      priceEl.innerText = `$${tPrice.toFixed(2)}`;
    } else {
        // Fallback for Salad/Wrap price
        const allSpans = Array.from(document.querySelectorAll('span, p'));
        const totalSpans = allSpans.filter(s => s.innerText.includes('$'));
        if (totalSpans.length) {
            totalSpans[totalSpans.length - 1].innerText = `$${tPrice.toFixed(2)}`;
        }
    }
    
    // Composition list
    const compEls = Array.from(document.querySelectorAll('p, h4, span, div')).filter(el => el.children.length === 0 && el.innerText.toUpperCase().includes('COMPOSITION'));
    if (compEls.length > 0) {
      const compParent = compEls[compEls.length - 1].parentElement;
      const compEl = compParent.querySelector('p:last-child');
      if (compEl && compEl !== compEls[compEls.length - 1]) {
        compEl.innerText = names.length > 0 ? names.join(', ') : 'Start selecting ingredients...';
      }
    }
  }

  // --- 5. CART INTEGRATION ---
  const cartBtn = document.querySelector('[data-purpose="add-to-cart-button"]');
  if (cartBtn) {
    cartBtn.addEventListener('click', () => {
      if (selectedItems.length === 0) {
        alert("Please select some ingredients first!");
        return;
      }
      
      let formatName = "Custom Meal";
      if (window.location.pathname.includes('salad')) formatName = "Fresh Salad";
      else if (window.location.pathname.includes('wrap')) formatName = "Artisan Wrap";
      else if (window.location.pathname.includes('smoothie')) formatName = "Super Smoothie";
      else formatName = "Signature Bowl";
      
      let tPrice = getFormatBasePrice();
      selectedItems.forEach(i => tPrice += i.price);
      
      const meal = {
        id: 'meal_' + Date.now(),
        name: formatName,
        price: tPrice,
        image: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=300&h=300&fit=crop',
        details: selectedItems.map(i => i.name).join(', ')
      };
      
      // Ensure cart.js functions exist
      if (window.Cart) {
        Cart.add(meal);
      } else {
        alert(`Added ${formatName} to cart!`);
      }
    });
  }

  // Initial zero-out sidebar
  updateSidebar();
});
