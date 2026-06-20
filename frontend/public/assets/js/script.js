'use strict';



/**
 * navbar toggle
 */

const navbar = document.querySelector("[data-navbar]");
const navbarLinks = document.querySelectorAll("[data-nav-link]");
const menuToggleBtn = document.querySelector("[data-menu-toggle-btn]");

if (menuToggleBtn && navbar) {
  menuToggleBtn.addEventListener("click", function () {
    navbar.classList.toggle("active");
    this.classList.toggle("active");
  });
}

for (let i = 0; i < navbarLinks.length; i++) {
  navbarLinks[i].addEventListener("click", function () {
    if (navbar && menuToggleBtn) {
      navbar.classList.toggle("active");
      menuToggleBtn.classList.toggle("active");
    }
  });
}



/**
 * header sticky & back to top
 */

const header = document.querySelector("[data-header]");
const backTopBtn = document.querySelector("[data-back-top-btn]");

window.addEventListener("scroll", function () {
  if (!header || !backTopBtn) return;
  if (window.scrollY >= 100) {
    header.classList.add("active");
    backTopBtn.classList.add("active");
  } else {
    header.classList.remove("active");
    backTopBtn.classList.remove("active");
  }
});







/**
 * move cycle on scroll
 */

const deliveryBoy = document.querySelector("[data-delivery-boy]");

let deliveryBoyMove = -80;
let lastScrollPos = 0;

window.addEventListener("scroll", function () {
  if (!deliveryBoy) return;

  let deliveryBoyTopPos = deliveryBoy.getBoundingClientRect().top;

  if (deliveryBoyTopPos < 500 && deliveryBoyTopPos > -250) {
    let activeScrollPos = window.scrollY;

    if (lastScrollPos < activeScrollPos) {
      deliveryBoyMove += 1;
    } else {
      deliveryBoyMove -= 1;
    }

    lastScrollPos = activeScrollPos;
    deliveryBoy.style.transform = `translateX(${deliveryBoyMove}px)`;
  }

});/**
 * menu filtering
 */

const filterBtns = document.querySelectorAll('[data-filter]');

filterBtns.forEach(btn => {
  btn.addEventListener('click', function () {
    // Remove active class from all buttons
    filterBtns.forEach(b => b.classList.remove('active'));
    // Add active class to clicked button
    this.classList.add('active');

    const filterValue = this.dataset.filter;
    const menuItems = document.querySelectorAll('.food-menu-list > li');

    menuItems.forEach(item => {
      if (filterValue === 'all') {
        item.style.display = 'block';
      } else {
        if (item.dataset.category === filterValue) {
          item.style.display = 'block';
        } else {
          item.style.display = 'none';
        }
      }
    });
  });
});

/**
 * promo card click to filter and scroll
 */
const promoCards = document.querySelectorAll('.promo-card');
promoCards.forEach(card => {
  card.style.cursor = 'pointer'; // Make it look clickable
  card.addEventListener('click', function () {
    // Get the title to match the category
    const title = this.querySelector('.card-title').textContent.toLowerCase();
    let category = 'all';

    if (title.includes('juices')) category = 'juices';
    else if (title.includes('smoothies')) category = 'smoothies';
    else if (title.includes('wraps')) category = 'wraps';
    else if (title.includes('salads')) category = 'salads';
    else if (title.includes('bowls')) category = 'bowls';

    // Find and click the corresponding filter button
    const targetBtn = document.querySelector(`[data-filter="${category}"]`);
    if (targetBtn) {
      targetBtn.click();
    }

    // Scroll to the menu section
    const menuSection = document.getElementById('food-menu');
    if (menuSection) {
      menuSection.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

/**
 * Menu "Order Now" buttons — add item to shared cart
 */
function attachOrderListeners() {
  document.querySelectorAll('.food-menu-card').forEach(card => {
    const btn = card.querySelector('.food-menu-btn');
    if (!btn) return;

    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();

      const productId = btn.dataset.id;
      const name = card.querySelector('.card-title')?.textContent || 'Menu Item';
      const category = card.querySelector('.category')?.textContent || '';
      const priceEl = card.querySelector('.price');
      const price = priceEl ? parseFloat(priceEl.getAttribute('value')) || 0 : 0;

      if (typeof Cart !== 'undefined') {
        Cart.add({ product_id: productId, name, category, price, details: category });
      }
    });
  });
}

async function loadProducts() {
  if (typeof getProducts !== 'function') {
    attachOrderListeners();
    return;
  }
  
  try {
    const products = await getProducts();
    const menuList = document.querySelector('.food-menu-list');
    if (!menuList) return;
    
    menuList.innerHTML = '';
    products.forEach(p => {
       const html = `
        <li data-category="${p.category.toLowerCase()}">
          <div class="food-menu-card">
            <div class="card-banner">
              <img src="${p.image_url || './assets/images/food-menu-1.png'}" width="300" height="300" loading="lazy" alt="${p.name}" class="w-100">
              <button class="btn food-menu-btn" data-id="${p.id}">Order Now</button>
            </div>
            <div class="wrapper">
              <p class="category">${p.category}</p>
              <div class="rating-wrapper">
                <ion-icon name="star"></ion-icon><ion-icon name="star"></ion-icon><ion-icon name="star"></ion-icon><ion-icon name="star"></ion-icon><ion-icon name="star"></ion-icon>
              </div>
            </div>
            <h3 class="h3 card-title">${p.name}</h3>
            <p class="card-text food-description">${p.description || ''}</p>
            <div class="price-wrapper">
              <p class="price-text">Price:</p>
              <data class="price" value="${p.price}">$${parseFloat(p.price).toFixed(2)}</data>
            </div>
          </div>
        </li>
       `;
       menuList.insertAdjacentHTML('beforeend', html);
    });

    attachOrderListeners();
  } catch(err) {
    console.error('Failed to load products', err);
    attachOrderListeners();
  }
}

document.addEventListener('DOMContentLoaded', loadProducts);

/**
 * Cart modal toggle (show/hide with display:flex)
 */
const cartModal = document.getElementById('cart-modal');
if (cartModal) {
  // Use CSS class to trigger sidebar animation
  const cartBtn = document.getElementById('cart-btn');
  const closeCart = document.getElementById('close-cart');

  if (cartBtn) {
    cartBtn.addEventListener('click', () => {
      cartModal.classList.add('open');
      if (typeof Cart !== 'undefined') Cart.renderDrawer();
    });
  }
  if (closeCart) {
    closeCart.addEventListener('click', () => {
      cartModal.classList.remove('open');
    });
  }
  cartModal.addEventListener('click', (e) => {
    if (e.target === cartModal) cartModal.classList.remove('open');
  });
}

/**
 * Hero text letter animation (Continuous Loop)
 */
document.addEventListener("DOMContentLoaded", () => {
  const heroTitle = document.querySelector(".hero-v2__title");
  if (!heroTitle) return;

  // Disable the parent fadeUp animation so it doesn't conflict with letters
  heroTitle.style.animation = "none";
  heroTitle.style.opacity = "1";

  const textLines = [
    { plain: "Real ", em: "Food" },
    { plain: "Real ", em: "Energy" },
    { plain: "Real ", em: "You" }
  ];

  function playAnimation() {
    let newHtml = "";
    let delay = 0.2; // Start after a short delay

    textLines.forEach(line => {
      // Plain text part
      for (let char of line.plain) {
        if (char === " ") {
          newHtml += " ";
        } else {
          newHtml += `<span class="letter-anim" style="animation-delay: ${delay}s">${char}</span>`;
          delay += 0.05;
        }
      }
      
      // Emphasized part
      newHtml += "<em>";
      for (let char of line.em) {
        newHtml += `<span class="letter-anim" style="animation-delay: ${delay}s">${char}</span>`;
        delay += 0.05;
      }
      newHtml += "</em><br>";
      delay += 0.2; // Pause before the next line
    });
    
    heroTitle.innerHTML = newHtml;
  }

  // Play immediately, then loop every 5 seconds
  playAnimation();
  setInterval(playAnimation, 5000);
});
