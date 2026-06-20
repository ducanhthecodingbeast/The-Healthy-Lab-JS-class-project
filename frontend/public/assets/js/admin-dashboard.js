const demoStaff = [
  { name: 'Chef', role: 'chef', shift: 'Morning', status: 'On duty' },
  { name: 'Delivery', role: 'delivery', shift: 'Evening', status: 'On duty' },
  { name: 'Cashier', role: 'staff', shift: 'Lunch rush', status: 'Standby' },
];

const demoReservations = [
  { customer_name: 'Linh Tran', customer_phone: '0901111000', party_size: 4, reservation_time: '2026-06-18 18:30', status: 'booked' },
  { customer_name: 'Minh Pham', customer_phone: '0902222000', party_size: 2, reservation_time: '2026-06-18 19:00', status: 'seated' },
];

const demoQueue = [
  { customer_name: 'Walk-in A12', party_size: 3, status: 'waiting', wait_minutes: 12 },
  { customer_name: 'Walk-in A13', party_size: 2, status: 'called', wait_minutes: 5 },
];

const demoInventory = [
  { name: 'Quinoa', unit: 'kg', stock: 8.5, low_stock_threshold: 5, expires_at: '2026-06-25' },
  { name: 'Avocado', unit: 'pcs', stock: 18, low_stock_threshold: 20, expires_at: '2026-06-20' },
  { name: 'Almond milk', unit: 'liters', stock: 12, low_stock_threshold: 6, expires_at: '2026-07-01' },
];

const demoSuppliers = [
  { name: 'Green Farm Co.', contact_name: 'Hoa', phone: '0903333000', item: 'Vegetables' },
  { name: 'Fresh Grain Supply', contact_name: 'Bao', phone: '0904444000', item: 'Quinoa, rice' },
];

const demoNotifications = [
  { title: 'Low stock', message: 'Avocado is below threshold.', level: 'warning' },
  { title: 'Expiry watch', message: 'Avocado batch expires soon.', level: 'info' },
];

const demoVouchers = [
  { code: 'GREEN10', description: '10% off healthy bowls', status: 'active' },
  { code: 'SMOOTHIE5', description: '$5 smoothie combo discount', status: 'draft' },
];

document.addEventListener('DOMContentLoaded', () => {
  if (!requireRole('admin')) return;

  loadSummary();
  loadOrders();
  loadProductsList();
  loadUsers();
  loadReportModules();
  renderAdminProfile();
});

function money(value) {
  return `$${Number(value || 0).toFixed(2)}`;
}

function statusPill(status) {
  return `<span class="status-pill">${String(status || 'n/a')}</span>`;
}

async function loadSummary() {
  const summary = await getAdminSummary();
  document.getElementById('summary-container').innerHTML = `
    <div class="summary-card"><h3>Total Orders</h3><p>${summary.total_orders}</p></div>
    <div class="summary-card"><h3>Pending</h3><p>${summary.pending_orders}</p></div>
    <div class="summary-card"><h3>Kitchen</h3><p>${summary.kitchen_orders || 0}</p></div>
    <div class="summary-card"><h3>Delivery</h3><p>${summary.delivery_orders || 0}</p></div>
    <div class="summary-card"><h3>Revenue</h3><p>${money(summary.total_revenue)}</p></div>
    <div class="summary-card"><h3>Customers</h3><p>${summary.total_customers}</p></div>
  `;
}

async function loadOrders() {
  const orders = await getAllOrders();
  const tbody = document.getElementById('orders-table');
  tbody.innerHTML = '';

  orders.forEach(order => {
    const itemNames = order.items.map(item => `${item.quantity}x ${item.product_name}`).join(', ');
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${order.id}</td>
      <td>${order.customer_name}</td>
      <td>${money(order.total_price)}</td>
      <td>
        <select onchange="updateAdminOrderStatus(${order.id}, this.value)">
          ${['pending', 'preparing', 'ready', 'delivering', 'delivered', 'cancelled'].map(status => `
            <option value="${status}" ${order.status === status ? 'selected' : ''}>${status}</option>
          `).join('')}
        </select>
      </td>
      <td><button class="btn-action" onclick="alert('${itemNames.replaceAll("'", "\\'")}')">Items</button></td>
    `;
    tbody.appendChild(tr);
  });
}

window.updateAdminOrderStatus = async function(id, status) {
  await updateOrderStatus(id, status);
  await loadOrders();
  await loadSummary();
};

async function loadProductsList() {
  const products = await getProducts(true);
  window.allProducts = products;
  const tbody = document.getElementById('products-table');
  tbody.innerHTML = '';

  products.forEach(product => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${product.id}</td>
      <td>${product.name}</td>
      <td>${product.category}</td>
      <td>${money(product.price)}</td>
      <td>${product.is_available ? 'Yes' : 'No'}</td>
      <td>
        <button class="btn-action" onclick="editProduct(${product.id})">Edit</button>
        <button class="btn-action ${product.is_available ? 'btn-danger' : 'btn-success'}" onclick="toggleProduct(${product.id}, ${!product.is_available})">
          ${product.is_available ? 'Disable' : 'Enable'}
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

window.editProduct = function(id) {
  const product = window.allProducts.find(item => item.id === id);
  if (!product) return;
  document.getElementById('p-id').value = product.id;
  document.getElementById('p-name').value = product.name;
  document.getElementById('p-category').value = product.category;
  document.getElementById('p-desc').value = product.description;
  document.getElementById('p-price').value = product.price;
  document.getElementById('p-cal').value = product.calories;
  document.getElementById('p-img').value = product.image_url || '';
  document.getElementById('product-form-title').textContent = 'Edit Product';
  document.getElementById('product-form').style.display = 'block';
};

window.toggleProduct = async function(id, is_available) {
  await updateProduct(id, { is_available });
  await loadProductsList();
  await loadSummary();
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

  if (id) {
    await updateProduct(id, data);
  } else {
    await createProduct(data);
  }
  document.getElementById('product-form').style.display = 'none';
  await loadProductsList();
  await loadSummary();
};

async function loadUsers() {
  const users = await getUsers();
  const tbody = document.getElementById('users-table');
  tbody.innerHTML = '';

  users.forEach(user => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td style="text-align:center;"><input type="checkbox"></td>
      <td>${user.id}</td>
      <td>${user.name}</td>
      <td>${user.email}</td>
      <td>${user.role}</td>
      <td>${user.phone || '-'}</td>
      <td style="width: 80px;">${statusPill(user.address ? 'profile' : 'missing')}</td>
    `;
    tbody.appendChild(tr);
  });
  document.getElementById('users-count-text').innerText = `${users.length} entries found`;
}

async function loadReportModules() {
  renderRows('staff-table', await getStaffProfiles() || demoStaff, ['name', 'role', 'shift', 'status']);
  renderRows('reservations-table', await getReservations() || demoReservations, ['customer_name', 'customer_phone', 'party_size', 'reservation_time', 'status']);
  renderRows('queue-table', await getQueueEntries() || demoQueue, ['customer_name', 'party_size', 'status', 'wait_minutes']);
  renderRows('inventory-table', await getInventoryItems() || demoInventory, ['name', 'stock', 'unit', 'low_stock_threshold', 'expires_at']);
  renderRows('suppliers-table', await getSuppliers() || demoSuppliers, ['name', 'contact_name', 'phone', 'item']);
  renderRows('notifications-table', await getNotifications() || demoNotifications, ['title', 'message', 'level']);
  renderRows('vouchers-table', await getVouchers() || demoVouchers, ['code', 'description', 'status']);
}

function renderRows(tbodyId, rows, fields) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  tbody.innerHTML = rows.map(row => `
    <tr>
      ${fields.map(field => `<td>${row[field] ?? '-'}</td>`).join('')}
    </tr>
  `).join('');
}

function renderAdminProfile() {
  const user = getCurrentUser();
  const label = document.getElementById('admin-profile-name');
  if (label && user) label.textContent = user.name;
}

window.toggleDropdown = function(e) {
  if (e) e.stopPropagation();
  const dropdown = document.getElementById('profile-dropdown');
  if (dropdown) dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
};

document.addEventListener('click', function(e) {
  const dropdown = document.getElementById('profile-dropdown');
  const container = document.querySelector('.profile-dropdown-container');
  if (dropdown && container && !container.contains(e.target)) {
    dropdown.style.display = 'none';
  }
});

window.switchView = function(viewId, el, e) {
  if (e) e.preventDefault();
  document.querySelectorAll('.view-section').forEach(section => {
    section.style.display = 'none';
  });
  const targetView = document.getElementById(viewId);
  if (targetView) targetView.style.display = 'block';

  const dropdown = document.getElementById('profile-dropdown');
  if (dropdown) dropdown.style.display = 'none';

  document.querySelectorAll('.strapi-sidebar-menu a').forEach(a => a.classList.remove('active'));
  if (el) el.classList.add('active');
};
