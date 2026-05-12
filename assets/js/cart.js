/**
 * SHARED CART SYSTEM — The Healthy Lab
 * Works on both index.html (menu orders) and food-lab.html (custom builds).
 * Persists to localStorage so the cart survives page navigation.
 */

'use strict';

const Cart = (() => {
  const STORAGE_KEY = 'healthylab_cart';

  /* ─── State ─── */
  let items = [];

  /* ─── LocalStorage ─── */
  function save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
  }

  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      items = raw ? JSON.parse(raw) : [];
    } catch {
      items = [];
    }
  }

  /* ─── Public API ─── */
  function add(item) {
    // item = { id, name, category, price, details }
    items.push({ ...item, id: Date.now() + Math.random() });
    save();
    renderBadge();
    renderDrawer();
    showToast(`${item.name} added to cart!`);
  }

  function remove(id) {
    items = items.filter(i => i.id !== id);
    save();
    renderBadge();
    renderDrawer();
  }

  function clear() {
    items = [];
    save();
    renderBadge();
    renderDrawer();
  }

  function getAll() {
    return items;
  }

  function getTotal() {
    return items.reduce((sum, i) => sum + (i.price || 0), 0);
  }

  /* ─── Badge (header cart icon counter) ─── */
  function renderBadge() {
    const badge = document.getElementById('cart-badge');
    if (!badge) return;
    if (items.length > 0) {
      badge.style.opacity = '1';
      badge.textContent = items.length;
    } else {
      badge.style.opacity = '0';
      badge.textContent = '0';
    }
  }

  /* ─── Cart Drawer / Modal ─── */
  function renderDrawer() {
    const container = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total-price');
    if (!container) return;

    container.innerHTML = '';

    if (items.length === 0) {
      container.innerHTML = '<p style="text-align:center; color:var(--text-muted, #999); font-size:1.4rem; padding:30px;">Your cart is empty.</p>';
    } else {
      items.forEach(item => {
        const el = document.createElement('div');
        el.className = 'cart-item';
        el.innerHTML = `
          <div class="cart-item-info">
            <h4 style="margin:0; font-size:1.6rem;">${item.name}</h4>
            <div class="cart-item-details" style="font-size:1.3rem; color:#888; margin-top:4px;">${item.details || item.category || ''}</div>
          </div>
          <div style="display:flex; align-items:center; gap:12px;">
            <span class="cart-item-price" style="font-size:1.6rem; font-weight:600;">$${item.price.toFixed(2)}</span>
            <button class="cart-remove-btn" data-cart-id="${item.id}" style="background:none; border:none; cursor:pointer; color:#e74c3c; font-size:1.8rem; line-height:1;" title="Remove">&times;</button>
          </div>
        `;
        container.appendChild(el);
      });

      // Attach remove handlers
      container.querySelectorAll('.cart-remove-btn').forEach(btn => {
        btn.addEventListener('click', function () {
          remove(Number(this.dataset.cartId));
        });
      });
    }

    if (totalEl) {
      totalEl.textContent = '$' + getTotal().toFixed(2);
    }
  }

  /* ─── Checkout flow ─── */
  function checkout() {
    if (items.length === 0) {
      showToast('Your cart is empty!');
      return;
    }

    const total = getTotal();
    const count = items.length;

    // Show a simple confirmation
    const confirmed = confirm(`Proceed to checkout?\n\n${count} item(s) — Total: $${total.toFixed(2)}\n\nThis is a demo — no real payment will be processed.`);

    if (confirmed) {
      showToast('Order placed successfully! Thank you!');
      clear();

      // Close the modal/drawer
      const modal = document.getElementById('cart-modal');
      if (modal) modal.classList.remove('active');
    }
  }

  /* ─── Toast Notification ─── */
  function showToast(msg) {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.style.cssText = 'position:fixed; bottom:30px; right:30px; z-index:9999; display:flex; flex-direction:column; gap:10px;';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.style.cssText = 'background:var(--cinnabar, #c8500a); color:white; padding:14px 24px; border-radius:8px; font-size:1.4rem; font-family:var(--ff-rubik, sans-serif); box-shadow:0 4px 20px rgba(0,0,0,0.2); animation:slideIn 0.3s ease;';
    toast.textContent = msg;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = 'slideOut 0.3s ease forwards';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  /* ─── Init ─── */
  function init() {
    load();
    renderBadge();

    // If a cart modal exists, set up its open/close
    const cartBtn = document.getElementById('cart-btn');
    const cartModal = document.getElementById('cart-modal');
    const closeCartBtn = document.getElementById('close-cart');

    if (cartBtn && cartModal) {
      cartBtn.addEventListener('click', () => {
        renderDrawer();
        cartModal.classList.add('active');
      });
    }
    if (closeCartBtn && cartModal) {
      closeCartBtn.addEventListener('click', () => cartModal.classList.remove('active'));
    }
    if (cartModal) {
      cartModal.addEventListener('click', (e) => {
        if (e.target === cartModal) cartModal.classList.remove('active');
      });
    }

    // "Proceed to Checkout" button
    const checkoutBtns = document.querySelectorAll('.checkout-proceed-btn');
    checkoutBtns.forEach(btn => btn.addEventListener('click', checkout));
  }

  return { init, add, remove, clear, getAll, getTotal, renderBadge, renderDrawer, showToast, checkout };
})();

document.addEventListener('DOMContentLoaded', Cart.init);
