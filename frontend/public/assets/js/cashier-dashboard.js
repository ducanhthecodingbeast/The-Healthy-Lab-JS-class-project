document.addEventListener('DOMContentLoaded', async () => {
  if (!requireRole('cashier')) return;

  const user = getCurrentUser();
  const nameEl = document.getElementById('cashier-profile-name');
  if (nameEl && user) nameEl.textContent = user.name;

  // View Switching
  window.switchView = function(viewId, element, event) {
    if (event) event.preventDefault();
    document.querySelectorAll('.view-section').forEach(el => el.style.display = 'none');
    document.getElementById(viewId).style.display = 'block';

    if (element) {
      document.querySelectorAll('.strapi-sidebar-menu a').forEach(el => el.classList.remove('active'));
      element.classList.add('active');
    }

    if (viewId === 'payments-view') loadPayments();
    else if (viewId === 'reservations-view') loadReservations();
    else if (viewId === 'queue-view') loadQueue();
    else if (viewId === 'tables-view') loadTables();
  };

  async function loadPayments() {
    const tbody = document.getElementById('payments-table');
    tbody.innerHTML = '<tr><td colspan="7">Loading...</td></tr>';
    try {
      const payments = await getPayments() || [];
      if (payments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7">No payments found</td></tr>';
        return;
      }
      tbody.innerHTML = payments.reverse().map(p => `
        <tr>
          <td>#${p.id}</td>
          <td>#${p.order_id}</td>
          <td>$${parseFloat(p.amount).toFixed(2)}</td>
          <td>${p.method}</td>
          <td><span class="status-badge status-${p.status}">${p.status.toUpperCase()}</span></td>
          <td>${new Date(p.created_at).toLocaleString()}</td>
          <td>
            <select onchange="updatePayment(${p.id}, this.value)" style="padding:4px; font-size:12px;">
              <option value="">Update Status...</option>
              <option value="paid" ${p.status === 'paid' ? 'disabled' : ''}>Mark Paid</option>
              <option value="failed" ${p.status === 'failed' ? 'disabled' : ''}>Mark Failed</option>
              <option value="refunded" ${p.status === 'refunded' ? 'disabled' : ''}>Mark Refunded</option>
            </select>
          </td>
        </tr>
      `).join('');
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="7" style="color:red">Error: ${err.message}</td></tr>`;
    }
  }

  window.updatePayment = async function(id, status) {
    if (!status) return;
    try {
      await updatePaymentStatus(id, status);
      loadPayments();
    } catch (err) {
      alert("Failed to update payment: " + err.message);
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
            <button onclick="completeRes(${r.id})" class="btn-action btn-primary" style="padding:4px 8px; font-size:12px;">Complete</button>
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
  }
  
  window.completeRes = async function(id) {
    try {
      await completeReservation(id);
      loadReservations();
    } catch(err) {
      alert("Failed: " + err.message);
    }
  }

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
  }

  window.seatQueue = async function(id) {
    try {
      await seatQueueEntry(id);
      loadQueue();
    } catch(err) {
      alert("Failed: " + err.message);
    }
  }

  window.cancelQueue = async function(id) {
    try {
      await updateQueueStatus(id, { status: 'cancelled' });
      loadQueue();
    } catch(err) {
      alert("Failed: " + err.message);
    }
  }

  async function loadTables() {
    const tbody = document.getElementById('tables-table');
    tbody.innerHTML = '<tr><td colspan="3">Loading...</td></tr>';
    try {
      const t = await getTables() || [];
      if (t.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3">No tables found</td></tr>';
        return;
      }
      tbody.innerHTML = t.map(item => `
        <tr>
          <td>${item.name}</td>
          <td>${item.capacity}</td>
          <td><span class="status-badge status-${item.status}">${item.status.toUpperCase()}</span></td>
        </tr>
      `).join('');
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="3" style="color:red">Error: ${err.message}</td></tr>`;
    }
  }

  // Load defaults
  loadPayments();
});
