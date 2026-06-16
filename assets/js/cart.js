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

  /* ─── Checkout flow ─── */
  function checkout() {
    if (items.length === 0) {
      showToast('Your cart is empty!');
      return;
    }

    if (typeof requireLogin === 'function' && !requireLogin()) {
      return; // Will redirect to login
    }

    const user = typeof getCurrentUser === 'function' ? getCurrentUser() : {};

    // Render form inside the cart modal
    const container = document.getElementById('cart-items');
    container.innerHTML = `
      <h3 style="margin-bottom: 15px; font-size: 1.8rem;">Checkout Details</h3>
      <form id="checkout-form" style="display: flex; flex-direction: column; gap: 10px;">
        <input type="text" id="co-name" placeholder="Full Name" required value="${user.name || ''}" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 1.4rem;">
        <input type="text" id="co-phone" placeholder="Phone Number" required value="${user.phone || ''}" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 1.4rem;">
        <input type="text" id="co-address" placeholder="Delivery Address" required value="${user.address || ''}" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 1.4rem;">
        <textarea id="co-note" placeholder="Order Note (e.g., Deliver after 6PM)" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 1.4rem; resize: vertical;"></textarea>
        <button type="submit" class="btn btn-hover" style="background-color:var(--cinnabar); color:white; padding:12px; font-size:1.6rem; border:none; border-radius:4px; margin-top: 10px; cursor:pointer;">Confirm Order</button>
      </form>
    `;

    // Hide normal footer
    const footerEl = document.querySelector('.modal-footer');
    if (footerEl) footerEl.style.display = 'none';

    document.getElementById('checkout-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const name = document.getElementById('co-name').value;
      const phone = document.getElementById('co-phone').value;
      const address = document.getElementById('co-address').value;
      const note = document.getElementById('co-note').value;
      
      const orderItems = items.map(i => {
        if (i.product_id) {
          return {
            product_id: parseInt(i.product_id),
            quantity: 1,
            custom_details: i.details || ''
          };
        } else {
          return {
            product_name: i.name,
            quantity: 1,
            unit_price: parseFloat(i.price),
            total_price: parseFloat(i.price),
            custom_details: i.details || ''
          };
        }
      });

      try {
        if (typeof createOrder === 'function') {
          await createOrder({
            customer_name: name,
            customer_phone: phone,
            delivery_address: address,
            note: note,
            items: orderItems
          });
          showToast('Order placed successfully!');
          clear();
          window.location.href = 'order-history.html';
        } else {
          showToast('createOrder API missing');
        }
      } catch (err) {
        showToast(err.message || 'Checkout failed');
      }
    });
  }

  /* ─── Cart Drawer / Modal ─── */
  function renderDrawer() {
    const container = document.getElementById('cart-items');
    const totalEl = document.getElementById('cart-total-price');
    const footerEl = document.querySelector('.modal-footer');
    if (footerEl) footerEl.style.display = 'block'; // Show footer normally
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
        cartModal.classList.add('open');
      });
    }
    if (closeCartBtn && cartModal) {
      closeCartBtn.addEventListener('click', () => cartModal.classList.remove('open'));
    }
    if (cartModal) {
      cartModal.addEventListener('click', (e) => {
        if (e.target === cartModal) cartModal.classList.remove('open');
      });
    }

    // "Proceed to Checkout" button
    const checkoutBtns = document.querySelectorAll('.checkout-proceed-btn');
    checkoutBtns.forEach(btn => btn.addEventListener('click', checkout));
  }

  return { init, add, remove, clear, getAll, getTotal, renderBadge, renderDrawer, showToast, checkout };
})();

document.addEventListener('DOMContentLoaded', Cart.init);
