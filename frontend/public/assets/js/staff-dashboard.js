document.addEventListener('DOMContentLoaded', async () => {
  if (!requireRole('staff')) return;

  const user = getCurrentUser();
  const nameEl = document.getElementById('staff-profile-name');
  if (nameEl && user) nameEl.textContent = user.name;

  window.switchView = function(viewId, element, event) {
    if (event) event.preventDefault();
    document.querySelectorAll('.view-section').forEach(el => el.style.display = 'none');
    document.getElementById(viewId).style.display = 'block';

    if (element) {
      document.querySelectorAll('.strapi-sidebar-menu a').forEach(el => el.classList.remove('active'));
      element.classList.add('active');
    }

    if (viewId === 'inventory-view') loadInventory();
    else if (viewId === 'lots-view') loadLots();
    else if (viewId === 'ingredients-view') loadIngredients();
    else if (viewId === 'suppliers-view') loadSuppliers();
    else if (viewId === 'reservations-view') loadReservations();
    else if (viewId === 'queue-view') loadQueue();
    else if (viewId === 'notifications-view') loadNotifications();
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

  async function loadLots() {
    const tbody = document.getElementById('lots-table');
    tbody.innerHTML = '<tr><td colspan="6">Loading...</td></tr>';
    try {
      const lots = await getInventoryLots() || [];
      if (lots.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6">No lots found</td></tr>';
        return;
      }
      tbody.innerHTML = lots.reverse().map(l => `
        <tr>
          <td>#${l.id}</td>
          <td>${l.ingredient_id}</td>
          <td>${l.supplier_id || ''}</td>
          <td>${l.quantity}</td>
          <td>$${parseFloat(l.unit_cost).toFixed(2)}</td>
          <td>${l.expires_at ? new Date(l.expires_at).toLocaleString() : 'N/A'}</td>
        </tr>
      `).join('');
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" style="color:red">Error: ${err.message}</td></tr>`;
    }
  }

  window.saveLot = async function() {
    try {
      await createInventoryLot({
        ingredient_id: parseInt(document.getElementById('lot-ingredient').value),
        supplier_id: document.getElementById('lot-supplier').value ? parseInt(document.getElementById('lot-supplier').value) : undefined,
        quantity: parseFloat(document.getElementById('lot-qty').value),
        unit_cost: parseFloat(document.getElementById('lot-cost').value),
        expires_at: document.getElementById('lot-expires').value || undefined
      });
      alert('Lot saved successfully');
      document.getElementById('lot-form').style.display = 'none';
      loadLots();
    } catch(err) {
      alert("Failed: " + err.message);
    }
  };

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

  window.saveIngredient = async function() {
    try {
      await createIngredient({
        name: document.getElementById('ing-name').value,
        unit: document.getElementById('ing-unit').value,
        low_stock_threshold: document.getElementById('ing-low').value ? parseFloat(document.getElementById('ing-low').value) : undefined
      });
      alert('Ingredient saved');
      document.getElementById('ingredient-form').style.display = 'none';
      loadIngredients();
    } catch(err) {
      alert("Failed: " + err.message);
    }
  };

  async function loadSuppliers() {
    const tbody = document.getElementById('suppliers-table');
    tbody.innerHTML = '<tr><td colspan="5">Loading...</td></tr>';
    try {
      const sup = await getSuppliers() || [];
      if (sup.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No suppliers found</td></tr>';
        return;
      }
      tbody.innerHTML = sup.map(s => `
        <tr>
          <td>#${s.id}</td>
          <td>${s.name}</td>
          <td>${s.contact_name || ''}</td>
          <td>${s.phone || ''}</td>
          <td>${s.item || ''}</td>
        </tr>
      `).join('');
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="5" style="color:red">Error: ${err.message}</td></tr>`;
    }
  }

  window.saveSupplier = async function() {
    try {
      await createSupplier({
        name: document.getElementById('sup-name').value,
        contact_name: document.getElementById('sup-contact').value || undefined,
        phone: document.getElementById('sup-phone').value || undefined,
        item: document.getElementById('sup-item').value || undefined
      });
      alert('Supplier saved');
      document.getElementById('supplier-form').style.display = 'none';
      loadSuppliers();
    } catch(err) {
      alert("Failed: " + err.message);
    }
  };

  async function loadReservations() {
    const tbody = document.getElementById('reservations-table');
    tbody.innerHTML = '<tr><td colspan="7">Loading...</td></tr>';
    try {
      const res = await getReservations() || [];
      if (res.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7">No reservations found</td></tr>';
        return;
      }
      tbody.innerHTML = res.reverse().map(r => `
        <tr>
          <td>#${r.id}</td>
          <td>${r.customer_name}</td>
          <td>${r.customer_phone}</td>
          <td>${r.party_size}</td>
          <td>${new Date(r.reservation_time).toLocaleString()}</td>
          <td><span class="status-badge status-${r.status}">${r.status.toUpperCase()}</span></td>
          <td>
            <select onchange="updateRes(${r.id}, this.value)" style="padding:4px; font-size:12px;">
              <option value="">Status...</option>
              <option value="seated">Seated</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </td>
        </tr>
      `).join('');
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="7" style="color:red">Error: ${err.message}</td></tr>`;
    }
  }

  window.updateRes = async function(id, status) {
    if (!status) return;
    try {
      await updateReservationStatus(id, status);
      loadReservations();
    } catch(err) {
      alert("Failed: " + err.message);
    }
  };

  async function loadQueue() {
    const tbody = document.getElementById('queue-table');
    tbody.innerHTML = '<tr><td colspan="6">Loading...</td></tr>';
    try {
      const q = await getQueueEntries() || [];
      if (q.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6">No queue entries found</td></tr>';
        return;
      }
      tbody.innerHTML = q.reverse().map(item => `
        <tr>
          <td>#${item.id}</td>
          <td>${item.customer_name}</td>
          <td>${item.party_size}</td>
          <td><span class="status-badge status-${item.status}">${item.status.toUpperCase()}</span></td>
          <td>${item.wait_minutes}</td>
          <td>
            <button onclick="seatQueue(${item.id})" class="btn-action btn-primary" style="padding:4px 8px; font-size:12px;">Seat</button>
            <button onclick="cancelQueue(${item.id})" class="btn-action btn-danger" style="padding:4px 8px; font-size:12px;">Cancel</button>
          </td>
        </tr>
      `).join('');
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" style="color:red">Error: ${err.message}</td></tr>`;
    }
  }

  window.callNext = async function() {
    try {
      await callNextQueueEntry();
      loadQueue();
    } catch(err) {
      alert("Failed: " + err.message);
    }
  };

  window.seatQueue = async function(id) {
    try {
      await seatQueueEntry(id);
      loadQueue();
    } catch(err) {
      alert("Failed: " + err.message);
    }
  };

  window.cancelQueue = async function(id) {
    try {
      await updateQueueStatus(id, { status: 'cancelled' });
      loadQueue();
    } catch(err) {
      alert("Failed: " + err.message);
    }
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

  // Initial load
  loadInventory();
});
