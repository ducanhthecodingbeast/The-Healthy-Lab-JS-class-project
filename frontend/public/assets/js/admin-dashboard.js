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
  const [summary, orders, payments] = await Promise.all([getAdminSummary(), getAllOrders(), getPayments()]);
  const orderSummary = orders.reduce((totals, order) => {
    totals.total_orders += 1;
    if (order.status === 'pending') totals.pending_orders += 1;
    if (order.status === 'preparing' || order.status === 'ready') totals.kitchen_orders += 1;
    if (order.status === 'delivering' || order.status === 'delivered') totals.delivery_orders += 1;
    return totals;
  }, { total_orders: 0, pending_orders: 0, kitchen_orders: 0, delivery_orders: 0 });
  const totalRevenue = (payments || []).reduce((sum, payment) => {
    return payment.status === 'paid' ? sum + Number(payment.amount || 0) : sum;
  }, 0);

  document.getElementById('summary-container').innerHTML = `
    <div class="summary-card"><h3>Total Orders</h3><p>${orderSummary.total_orders}</p></div>
    <div class="summary-card"><h3>Pending</h3><p>${orderSummary.pending_orders}</p></div>
    <div class="summary-card"><h3>Kitchen</h3><p>${orderSummary.kitchen_orders}</p></div>
    <div class="summary-card"><h3>Delivery</h3><p>${orderSummary.delivery_orders}</p></div>
    <div class="summary-card"><h3>Revenue</h3><p>${money(totalRevenue)}</p></div>
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
  loadStaff();
  loadReservations();
  loadQueue();
  loadInventory();
  loadLots();
  loadSuppliers();
  loadIngredients();
  loadTables();
  loadPayments();
}

window.loadStaff = async function() {
  const tbody = document.getElementById('staff-table');
  if(!tbody) return;
  tbody.innerHTML = '<tr><td colspan="4">Loading...</td></tr>';
  try {
    const data = await getStaffProfiles() || demoStaff;
    tbody.innerHTML = data.map(r => `<tr><td>${r.name}</td><td>${r.role}</td><td>${r.shift}</td><td>${r.status}</td></tr>`).join('');
  } catch(e) {}
};

window.saveStaff = async function() {
  try {
    await createStaffProfile({
      name: document.getElementById('stf-name').value,
      role: document.getElementById('stf-role').value,
      shift: document.getElementById('stf-shift').value,
      status: document.getElementById('stf-status').value,
      user_id: document.getElementById('stf-userid').value ? parseInt(document.getElementById('stf-userid').value) : undefined
    });
    alert('Staff profile created');
    document.getElementById('staff-form').style.display='none';
    loadStaff();
  } catch(err) { alert("Failed: " + err.message); }
};

window.loadReservations = async function() {
  const tbody = document.getElementById('reservations-table');
  if(!tbody) return;
  try {
    const data = await getReservations() || [];
    tbody.innerHTML = data.map(r => `
      <tr>
        <td>#${r.id}</td><td>${r.customer_name}</td><td>${r.customer_phone}</td><td>${r.party_size}</td>
        <td>${new Date(r.reservation_time).toLocaleString()}</td>
        <td><span class="status-badge status-${r.status}">${r.status}</span></td>
        <td>
          <select onchange="updateRes(${r.id}, this.value)">
            <option value="">Status...</option><option value="seated">Seated</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option>
          </select>
        </td>
      </tr>
    `).join('');
  } catch(e) {}
};

window.updateRes = async function(id, status) {
  if(!status) return;
  try {
    await updateReservationStatus(id, status);
    loadReservations();
  } catch(err) { alert(err.message); }
};

window.loadQueue = async function() {
  const tbody = document.getElementById('queue-table');
  if(!tbody) return;
  try {
    const data = await getQueueEntries() || [];
    tbody.innerHTML = data.map(item => `
      <tr>
        <td>#${item.id}</td><td>${item.customer_name}</td><td>${item.party_size}</td>
        <td><span class="status-badge status-${item.status}">${item.status}</span></td>
        <td>${item.wait_minutes}</td>
        <td>
          <button onclick="seatQueue(${item.id})" class="btn-action btn-primary">Seat</button>
          <button onclick="cancelQueue(${item.id})" class="btn-action btn-danger">Cancel</button>
        </td>
      </tr>
    `).join('');
  } catch(e) {}
};

window.adminCallNextQueue = async function() {
  try {
    await callNextQueueEntry();
    loadQueue();
  } catch(err) { alert(err.message); }
};
window.seatQueue = async function(id) {
  try { await seatQueueEntry(id); loadQueue(); } catch(err) { alert(err.message); }
};
window.cancelQueue = async function(id) {
  try { await updateQueueStatus(id, {status:'cancelled'}); loadQueue(); } catch(err) { alert(err.message); }
};

window.loadInventory = async function() {
  const tbody = document.getElementById('inventory-table');
  if(!tbody) return;
  try {
    const data = await getInventoryItems() || demoInventory;
    tbody.innerHTML = data.map(r => `<tr><td>${r.name || r.ingredient_name}</td><td>${r.stock}</td><td>${r.unit}</td><td>${r.low_stock_threshold}</td><td>${r.expires_at||'N/A'}</td></tr>`).join('');
  } catch(e) {}
};

window.loadLots = async function() {
  const tbody = document.getElementById('lots-table');
  if(!tbody) return;
  try {
    const data = await getInventoryLots() || [];
    tbody.innerHTML = data.map(l => `<tr><td>#${l.id}</td><td>${l.ingredient_id}</td><td>${l.supplier_id||''}</td><td>${l.quantity}</td><td>$${l.unit_cost}</td><td>${l.expires_at||'N/A'}</td></tr>`).join('');
  } catch(e) {}
};

window.adminSaveLot = async function() {
  try {
    await createInventoryLot({
      ingredient_id: parseInt(document.getElementById('lot-ingredient').value),
      supplier_id: document.getElementById('lot-supplier').value ? parseInt(document.getElementById('lot-supplier').value) : undefined,
      quantity: parseFloat(document.getElementById('lot-qty').value),
      unit_cost: parseFloat(document.getElementById('lot-cost').value),
      expires_at: document.getElementById('lot-expires').value || undefined
    });
    document.getElementById('lot-form').style.display='none';
    loadLots();
  } catch(err) { alert(err.message); }
};

window.loadSuppliers = async function() {
  const tbody = document.getElementById('suppliers-table');
  if(!tbody) return;
  try {
    const data = await getSuppliers() || demoSuppliers;
    tbody.innerHTML = data.map(s => `<tr><td>#${s.id||'-'}</td><td>${s.name}</td><td>${s.contact_name||'-'}</td><td>${s.phone||'-'}</td><td>${s.item||'-'}</td></tr>`).join('');
  } catch(e) {}
};

window.adminSaveSupplier = async function() {
  try {
    await createSupplier({
      name: document.getElementById('sup-name').value,
      contact_name: document.getElementById('sup-contact').value || undefined,
      phone: document.getElementById('sup-phone').value || undefined,
      item: document.getElementById('sup-item').value || undefined
    });
    document.getElementById('supplier-form').style.display='none';
    loadSuppliers();
  } catch(err) { alert(err.message); }
};

window.loadIngredients = async function() {
  const tbody = document.getElementById('ingredients-table');
  if(!tbody) return;
  try {
    const data = await getIngredients() || [];
    tbody.innerHTML = data.map(i => `<tr><td>#${i.id}</td><td>${i.name}</td><td>${i.unit}</td><td>${i.low_stock_threshold||''}</td></tr>`).join('');
  } catch(e) {}
};

window.adminSaveIngredient = async function() {
  try {
    await createIngredient({
      name: document.getElementById('ing-name').value,
      unit: document.getElementById('ing-unit').value,
      low_stock_threshold: document.getElementById('ing-low').value ? parseFloat(document.getElementById('ing-low').value) : undefined
    });
    document.getElementById('ingredient-form').style.display='none';
    loadIngredients();
  } catch(err) { alert(err.message); }
};

window.loadTables = async function() {
  const tbody = document.getElementById('tables-table');
  if(!tbody) return;
  try {
    const data = await getTables() || [];
    tbody.innerHTML = data.map(t => `<tr><td>${t.name}</td><td>${t.capacity}</td><td><span class="status-badge status-${t.status}">${t.status}</span></td></tr>`).join('');
  } catch(e) {}
};

window.adminSaveTable = async function() {
  try {
    await createTable({
      name: document.getElementById('tbl-name').value,
      capacity: parseInt(document.getElementById('tbl-capacity').value),
      status: document.getElementById('tbl-status').value
    });
    document.getElementById('table-form').style.display='none';
    loadTables();
  } catch(err) { alert(err.message); }
};

window.loadPayments = async function() {
  const tbody = document.getElementById('payments-table');
  if(!tbody) return;
  try {
    const data = await getPayments() || [];
    tbody.innerHTML = data.map(p => `
      <tr>
        <td>#${p.id}</td><td>#${p.order_id}</td><td>$${p.amount}</td><td>${p.method}</td>
        <td><span class="status-badge status-${p.status}">${p.status}</span></td>
        <td>
          <select onchange="updatePayment(${p.id}, this.value)">
            <option value="">Status...</option><option value="paid">Paid</option><option value="failed">Failed</option><option value="refunded">Refunded</option>
          </select>
        </td>
      </tr>
    `).join('');
  } catch(e) {}
};

window.updatePayment = async function(id, status) {
  if(!status) return;
  try {
    await updatePaymentStatus(id, status);
    loadPayments();
  } catch(err) { alert(err.message); }
};

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
