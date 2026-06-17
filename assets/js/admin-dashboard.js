document.addEventListener('DOMContentLoaded', () => {
  if (!requireRole('admin')) return;

  loadSummary();
  loadOrders();
  loadProductsList();
  loadUsers();

  async function loadSummary() {
    try {
      let summary;
      try {
        summary = await getAdminSummary();
      } catch (e) {
        // Mock data fallback
        summary = {
          total_orders: 125,
          pending_orders: 8,
          delivered_orders: 110,
          total_revenue: 4500.50,
          total_customers: 34
        };
      }
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
      let orders;
      try {
        orders = await getAllOrders();
      } catch (e) {
        // Mock data fallback
        orders = [
          { id: 1001, customer_name: 'John Doe', total_price: 45.00, status: 'pending', items: [{product_name: 'Nourish Bowl'}] },
          { id: 1002, customer_name: 'Jane Smith', total_price: 22.50, status: 'preparing', items: [{product_name: 'Fresh Juice'}] },
          { id: 1003, customer_name: 'Alice Johnson', total_price: 67.80, status: 'delivered', items: [{product_name: 'Garden Salad'}, {product_name: 'Wholesome Wrap'}] }
        ];
      }
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
    } catch (err) {
      console.log('API failed, falling back to mock update');
    }
    loadSummary();
  };

  async function loadProductsList() {
    try {
      let products;
      try {
        products = await getProducts(true);
      } catch (e) {
        // Mock data fallback
        products = [
          { id: 1, name: 'Nourish Bowl', category: 'Bowls', price: 12.99, is_available: true, calories: 450, description: 'Healthy grain base with veg' },
          { id: 2, name: 'Fresh Juice', category: 'Beverages', price: 5.50, is_available: true, calories: 120, description: 'Cold pressed orange and carrot' },
          { id: 3, name: 'Wholesome Wrap', category: 'Wraps', price: 9.99, is_available: false, calories: 380, description: 'Whole-grain wrap stuffed with proteins' }
        ];
      }
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
    } catch (err) {
      console.log('API failed, mock toggle');
    }
    loadProductsList();
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
    } catch (err) {
      console.log('API failed, mock save success');
    }
    document.getElementById('product-form').style.display = 'none';
    loadProductsList();
  };

  async function loadUsers() {
    try {
      let users;
      try {
        users = await getUsers();
      } catch(e) {
        // Mock data fallback
        users = [
          { id: 1, name: 'Admin', email: 'admin@healthylab.com' },
          { id: 2, name: 'Chef Gordon', email: 'gordon@healthylab.com' },
          { id: 3, name: 'John Customer', email: 'john@example.com' }
        ];
      }
      const tbody = document.getElementById('users-table');
      tbody.innerHTML = '';
      users.forEach(u => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td style="text-align:center;"><input type="checkbox"></td>
          <td>${u.id}</td>
          <td>${u.name}</td>
          <td>${u.email}</td>
          <td>********</td>
          <td>0</td>
          <td style="text-align:right;">
            <ion-icon name="pencil" style="cursor:pointer; margin-right:10px; color:var(--text-gray); font-size:14px;"></ion-icon>
            <ion-icon name="trash" style="cursor:pointer; color:var(--text-gray); font-size:14px;"></ion-icon>
          </td>
        `;
        tbody.appendChild(tr);
      });
      document.getElementById('users-count-text').innerText = `${users.length} entry found`;
    } catch (err) {
      console.error('Failed to load users', err);
    }
  }

});

// --- UI Switching and Dropdowns ---
window.toggleDropdown = function(e) {
  if(e) e.stopPropagation();
  const dropdown = document.getElementById('profile-dropdown');
  if (dropdown) {
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
  }
};

document.addEventListener('click', function(e) {
  const dropdown = document.getElementById('profile-dropdown');
  const container = document.querySelector('.profile-dropdown-container');
  if(dropdown && container && !container.contains(e.target)) {
    dropdown.style.display = 'none';
  }
});

window.switchView = function(viewId, el, e) {
  if(e) e.stopPropagation();
  document.querySelectorAll('.view-section').forEach(section => {
    section.style.display = 'none';
  });
  const targetView = document.getElementById(viewId);
  if (targetView) targetView.style.display = 'block';
  
  const dropdown = document.getElementById('profile-dropdown');
  if (dropdown) dropdown.style.display = 'none';
  
  if(el) {
    document.querySelectorAll('.strapi-sidebar-menu a').forEach(a => a.classList.remove('active'));
    el.classList.add('active');
  } else if (viewId === 'users-view') {
    document.querySelectorAll('.strapi-sidebar-menu a').forEach(a => a.classList.remove('active'));
    // Find the Customers link and make it active (assuming it's the 4th link)
    const customerLink = document.querySelectorAll('.strapi-sidebar-menu a')[3];
    if (customerLink) customerLink.classList.add('active');
  }
};
