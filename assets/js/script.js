'use strict';



/**
 * navbar toggle
 */

const navbar = document.querySelector("[data-navbar]");
const navbarLinks = document.querySelectorAll("[data-nav-link]");
const menuToggleBtn = document.querySelector("[data-menu-toggle-btn]");

menuToggleBtn.addEventListener("click", function () {
  navbar.classList.toggle("active");
  this.classList.toggle("active");
});

for (let i = 0; i < navbarLinks.length; i++) {
  navbarLinks[i].addEventListener("click", function () {
    navbar.classList.toggle("active");
    menuToggleBtn.classList.toggle("active");
  });
}



/**
 * header sticky & back to top
 */

const header = document.querySelector("[data-header]");
const backTopBtn = document.querySelector("[data-back-top-btn]");

window.addEventListener("scroll", function () {
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
const menuItems = document.querySelectorAll('.food-menu-list > li');

filterBtns.forEach(btn => {
  btn.addEventListener('click', function () {
    // Remove active class from all buttons
    filterBtns.forEach(b => b.classList.remove('active'));
    // Add active class to clicked button
    this.classList.add('active');

    const filterValue = this.dataset.filter;

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
  card.addEventListener('click', function() {
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
document.querySelectorAll('.food-menu-card').forEach(card => {
  const btn = card.querySelector('.food-menu-btn');
  if (!btn) return;

  btn.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();

    const name = card.querySelector('.card-title')?.textContent || 'Menu Item';
    const category = card.querySelector('.category')?.textContent || '';
    const priceEl = card.querySelector('.price');
    const price = priceEl ? parseFloat(priceEl.getAttribute('value')) || 0 : 0;

    if (typeof Cart !== 'undefined') {
      Cart.add({ name, category, price, details: category });
    }
  });
});

/**
 * Cart modal toggle (show/hide with display:flex)
 */
const cartModal = document.getElementById('cart-modal');
if (cartModal) {
  // Override click handlers to use display instead of class
  const cartBtn = document.getElementById('cart-btn');
  const closeCart = document.getElementById('close-cart');

  if (cartBtn) {
    cartBtn.addEventListener('click', () => {
      cartModal.style.display = 'flex';
      if (typeof Cart !== 'undefined') Cart.renderDrawer();
    });
  }
  if (closeCart) {
    closeCart.addEventListener('click', () => {
      cartModal.style.display = 'none';
    });
  }
  cartModal.addEventListener('click', (e) => {
    if (e.target === cartModal) cartModal.style.display = 'none';
  });
}

