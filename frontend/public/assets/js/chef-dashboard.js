document.addEventListener('DOMContentLoaded', () => {
  if (!requireRole('chef')) return;

  const container = document.getElementById('orders-container');

  async function loadOrders() {
    try {
      const allOrders = await getAllOrders();
      // Chef only sees pending and preparing orders
      const orders = allOrders.filter(o => o.status === 'pending' || o.status === 'preparing');
      
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
          actionBtn = `<button class="action-btn" onclick="updateStatus(${order.id}, 'preparing')">Start Preparing</button>`;
        } else if (order.status === 'preparing') {
          actionBtn = `<button class="action-btn ready" onclick="updateStatus(${order.id}, 'ready')">Mark as Ready</button>`;
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

  loadOrders();
});
