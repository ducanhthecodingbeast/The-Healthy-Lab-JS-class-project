document.addEventListener('DOMContentLoaded', async () => {
  if (!requireRole('chef')) return;

  const user = getCurrentUser();
  const nameEl = document.getElementById('chef-profile-name');
  if (nameEl && user) nameEl.textContent = user.name;

  const container = document.getElementById('orders-container');
  const statActive = document.getElementById('stat-active');

  window.switchView = function(viewId, element, event) {
    if (event) event.preventDefault();
    document.querySelectorAll('.view-section').forEach(el => el.style.display = 'none');
    document.getElementById(viewId).style.display = 'block';

    if (element) {
      document.querySelectorAll('.strapi-sidebar-menu a').forEach(el => el.classList.remove('active'));
      element.classList.add('active');
    }

    if (viewId === 'orders-view') loadOrders();
    else if (viewId === 'inventory-view') loadInventory();
    else if (viewId === 'ingredients-view') loadIngredients();
    else if (viewId === 'recipes-view') loadRecipes();
    else if (viewId === 'notifications-view') loadNotifications();
  };

  async function loadOrders() {
    try {
      const allOrders = await getAllOrders();
      const orders = allOrders.filter(o => o.status === 'pending' || o.status === 'preparing');
      
      if (statActive) statActive.textContent = orders.length;

      if (orders.length === 0) {
        container.innerHTML = '<p style="font-size: 1.6rem; color: #666;">No orders require kitchen attention right now.</p>';
        return;
      }

      container.innerHTML = '';
      orders.forEach(order => {
        let itemsHtml = order.items.map(i => `
          <div style="font-size: 1.4rem; color: #333; margin-bottom: 8px; padding-left: 10px; border-left: 2px solid #ccc;">
            <strong style="font-size: 1.5rem;">${i.quantity}x ${i.product_name}</strong>
            ${i.custom_details ? `<br><span style="color:var(--cinnabar); font-weight:500;">Details: ${i.custom_details}</span>` : ''}
          </div>
        `).join('');

        let actionBtn = '';
        if (order.status === 'pending') {
          actionBtn = `<button class="btn-action btn-primary" onclick="updateStatus(${order.id}, 'preparing')">Start Preparing</button>`;
        } else if (order.status === 'preparing') {
          actionBtn = `<button class="btn-action btn-success" onclick="updateStatus(${order.id}, 'ready')">Mark as Ready</button>`;
        }

        const html = `
          <div class="order-card ${order.status}">
            <div class="order-header">
              <div>
                <span style="font-size: 1.8rem; font-weight: bold;">Order #${order.id}</span>
                <span style="font-size: 1.4rem; color: #666; margin-left: 10px;">${order.customer_name}</span>
              </div>
              <span class="status-badge status-${order.status}">${order.status}</span>
            </div>
            <div style="margin-bottom: 15px;">
              ${itemsHtml}
            </div>
            ${order.note ? `<div style="font-size: 1.3rem; color: #888; margin-bottom: 10px; font-style: italic;">Note: ${order.note}</div>` : ''}
            <div style="text-align: right;">
              ${actionBtn}
            </div>
          </div>
        `;
        container.insertAdjacentHTML('beforeend', html);
      });
    } catch (err) {
      container.innerHTML = `<p style="color: red; font-size: 1.6rem;">Error loading orders: ${err.message}</p>`;
    }
  }

  window.updateStatus = async function(id, status) {
    try {
      await updateOrderStatus(id, status);
      loadOrders();
    } catch (err) {
      alert('Failed to update status: ' + err.message);
    }
  };

  async function loadInventory() {
    const tbody = document.getElementById('inventory-table');
    tbody.innerHTML = '<tr><td colspan="5">Loading...</td></tr>';
    try {
      const inv = await getInventoryItems() || [];
      if (inv.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No inventory found</td></tr>';
        return;
      }
      tbody.innerHTML = inv.map(item => `
        <tr>
          <td>${item.ingredient_name || item.name}</td>
          <td>${item.stock}</td>
          <td>${item.unit || ''}</td>
          <td>${item.low_stock_threshold || ''}</td>
          <td>${item.expires_at ? new Date(item.expires_at).toLocaleDateString() : 'N/A'}</td>
        </tr>
      `).join('');
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="5" style="color:red">Error: ${err.message}</td></tr>`;
    }
  }

  async function loadIngredients() {
    const tbody = document.getElementById('ingredients-table');
    tbody.innerHTML = '<tr><td colspan="4">Loading...</td></tr>';
    try {
      const ing = await getIngredients() || [];
      if (ing.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4">No ingredients found</td></tr>';
        return;
      }
      tbody.innerHTML = ing.map(i => `
        <tr>
          <td>#${i.id}</td>
          <td>${i.name}</td>
          <td>${i.unit}</td>
          <td>${i.low_stock_threshold || ''}</td>
        </tr>
      `).join('');
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="4" style="color:red">Error: ${err.message}</td></tr>`;
    }
  }

  async function loadRecipes() {
    const tbody = document.getElementById('recipes-table');
    tbody.innerHTML = '<tr><td colspan="4">Loading...</td></tr>';
    try {
      // populate form dropdowns
      const [products, ingredients, recipes] = await Promise.all([
        getProducts(),
        getIngredients(),
        getRecipes()
      ]);
      
      const pSelect = document.getElementById('rec-product');
      if(products) pSelect.innerHTML = '<option value="">Select Product...</option>' + products.map(p=>`<option value="${p.id}">${p.name}</option>`).join('');
      
      const iSelect = document.getElementById('rec-ingredient');
      if(ingredients) iSelect.innerHTML = '<option value="">Select Ingredient...</option>' + ingredients.map(i=>`<option value="${i.id}">${i.name} (${i.unit})</option>`).join('');

      if (!recipes || recipes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4">No recipes found</td></tr>';
        return;
      }
      tbody.innerHTML = recipes.reverse().map(r => `
        <tr>
          <td>#${r.id}</td>
          <td>${r.product_id}</td>
          <td>${r.ingredient_id}</td>
          <td>${r.quantity}</td>
        </tr>
      `).join('');
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="4" style="color:red">Error: ${err.message}</td></tr>`;
    }
  }

  window.saveRecipe = async function() {
    try {
      await createRecipeItem({
        product_id: parseInt(document.getElementById('rec-product').value),
        ingredient_id: parseInt(document.getElementById('rec-ingredient').value),
        quantity: parseFloat(document.getElementById('rec-qty').value)
      });
      alert('Recipe item added');
      document.getElementById('recipe-form').style.display='none';
      loadRecipes();
    } catch(err) { alert(err.message); }
  };

  async function loadNotifications() {
    const tbody = document.getElementById('notifications-table');
    tbody.innerHTML = '<tr><td colspan="4">Loading...</td></tr>';
    try {
      const notifs = await getNotifications() || [];
      if (notifs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4">No notifications found</td></tr>';
        return;
      }
      tbody.innerHTML = notifs.reverse().map(n => `
        <tr>
          <td><span class="status-badge status-${n.level}">${n.level.toUpperCase()}</span></td>
          <td>${n.title}</td>
          <td>${n.message}</td>
          <td>${new Date(n.created_at).toLocaleString()}</td>
        </tr>
      `).join('');
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="4" style="color:red">Error: ${err.message}</td></tr>`;
    }
  }

  loadOrders();
});
