document.addEventListener('DOMContentLoaded', () => {
  if (!requireRole('admin')) return;

  loadSummary();
  loadOrders();
  loadProductsList();
  loadUsers();

  async function loadSummary() {
    try {
      const summary = await getAdminSummary();
      document.getElementById('summary-container').innerHTML = `
        <div class="summary-card"><h3>Total Orders</h3><p>${summary.total_orders}</p></div>
        <div class="summary-card"><h3>Pending Orders</h3><p>${summary.pending_orders}</p></div>
        <div class="summary-card"><h3>Delivered Orders</h3><p>${summary.delivered_orders}</p></div>
        <div class="summary-card"><h3>Total Revenue</h3><p>$${summary.total_revenue.toFixed(2)}</p></div>
        <div class="summary-card"><h3>Total Customers</h3><p>${summary.total_customers}</p></div>
      `;
    } catch (err) {
      console.error('Failed to load summary', err);
    }
  }

  async function loadOrders() {
    try {
      const orders = await getAllOrders();
      const tbody = document.getElementById('orders-table');
      tbody.innerHTML = '';
      orders.forEach(o => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${o.id}</td>
          <td>${o.customer_name}</td>
          <td>$${o.total_price.toFixed(2)}</td>
          <td>
            <select onchange="updateAdminOrderStatus(${o.id}, this.value)" style="padding: 5px; border-radius: 4px;">
              <option value="pending" ${o.status === 'pending' ? 'selected' : ''}>Pending</option>
              <option value="preparing" ${o.status === 'preparing' ? 'selected' : ''}>Preparing</option>
              <option value="ready" ${o.status === 'ready' ? 'selected' : ''}>Ready</option>
              <option value="delivering" ${o.status === 'delivering' ? 'selected' : ''}>Delivering</option>
              <option value="delivered" ${o.status === 'delivered' ? 'selected' : ''}>Delivered</option>
              <option value="cancelled" ${o.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
            </select>
          </td>
          <td><button class="btn-action" onclick="alert('Details for order ${o.id}: \\n' + '${o.items.map(i => i.product_name).join(', ')}')">Items</button></td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      console.error('Failed to load orders', err);
    }
  }

  window.updateAdminOrderStatus = async function(id, status) {
    try {
      await updateOrderStatus(id, status);
      loadSummary();
    } catch (err) {
      alert('Failed to update order status');
    }
  };

  async function loadProductsList() {
    try {
      const products = await getProducts(true);
      window.allProducts = products;
      const tbody = document.getElementById('products-table');
      tbody.innerHTML = '';
      products.forEach(p => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${p.id}</td>
          <td>${p.name}</td>
          <td>${p.category}</td>
          <td>$${p.price.toFixed(2)}</td>
          <td>${p.is_available ? 'Yes' : 'No'}</td>
          <td>
            <button class="btn-action" onclick="editProduct(${p.id})">Edit</button>
            <button class="btn-action ${p.is_available ? 'btn-danger' : 'btn-success'}" onclick="toggleProduct(${p.id}, ${!p.is_available})">
              ${p.is_available ? 'Disable' : 'Enable'}
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      console.error('Failed to load products', err);
    }
  }

  window.editProduct = function(id) {
    const p = window.allProducts.find(x => x.id === id);
    if (!p) return;
    document.getElementById('p-id').value = p.id;
    document.getElementById('p-name').value = p.name;
    document.getElementById('p-category').value = p.category;
    document.getElementById('p-desc').value = p.description;
    document.getElementById('p-price').value = p.price;
    document.getElementById('p-cal').value = p.calories;
    document.getElementById('p-img').value = p.image_url || '';
    document.getElementById('product-form-title').textContent = 'Edit Product';
    document.getElementById('product-form').style.display = 'block';
  };

  window.toggleProduct = async function(id, is_available) {
    try {
      await updateProduct(id, { is_available });
      loadProductsList();
    } catch (err) {
      alert('Failed to toggle product status');
    }
  };

  window.saveProduct = async function() {
    const id = document.getElementById('p-id').value;
    const data = {
      name: document.getElementById('p-name').value,
      category: document.getElementById('p-category').value,
      description: document.getElementById('p-desc').value,
      price: parseFloat(document.getElementById('p-price').value),
      calories: parseInt(document.getElementById('p-cal').value),
      image_url: document.getElementById('p-img').value || null
    };

    try {
      if (id) {
        await updateProduct(id, data);
      } else {
        await createProduct(data);
      }
      document.getElementById('product-form').style.display = 'none';
      loadProductsList();
    } catch (err) {
      alert('Failed to save product: ' + err.message);
    }
  };

  async function loadUsers() {
    try {
      const users = await getUsers();
      const tbody = document.getElementById('users-table');
      tbody.innerHTML = '';
      users.forEach(u => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${u.id}</td>
          <td>${u.name}</td>
          <td>${u.email}</td>
          <td><span style="background:#eee; padding:3px 8px; border-radius:4px;">${u.role}</span></td>
        `;
        tbody.appendChild(tr);
      });
    } catch (err) {
      console.error('Failed to load users', err);
    }
  }
});
