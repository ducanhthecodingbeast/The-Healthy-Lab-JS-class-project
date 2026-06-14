document.addEventListener('DOMContentLoaded', async () => {
  if (!requireRole('customer')) return;

  const container = document.getElementById('orders-container');

  async function loadOrders() {
    try {
      const orders = await getMyOrders();
      if (orders.length === 0) {
        container.innerHTML = '<p style="font-size: 1.6rem; color: #666;">You have no orders yet.</p>';
        return;
      }

      container.innerHTML = '';
      orders.reverse().forEach(order => {
        let itemsHtml = order.items.map(i => `
          <div style="font-size: 1.4rem; color: #555; display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span>${i.quantity}x ${i.product_name} ${i.custom_details ? `<br><small style="color:#888;">${i.custom_details}</small>` : ''}</span>
            <span>$${i.total_price.toFixed(2)}</span>
          </div>
        `).join('');

        let cancelBtn = '';
        if (order.status === 'pending') {
          cancelBtn = `<button onclick="cancelOrder(${order.id})" style="background: #e74c3c; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">Cancel Order</button>`;
        }

        const html = `
          <div class="order-card">
            <div class="order-header">
              <span style="font-size: 1.6rem; font-weight: bold;">Order #${order.id}</span>
              <span class="status-badge status-${order.status}">${order.status.toUpperCase()}</span>
            </div>
            <div style="margin-bottom: 10px;">
              ${itemsHtml}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #eee; padding-top: 10px;">
              <span style="font-size: 1.8rem; font-weight: bold; color: var(--cinnabar);">Total: $${order.total_price.toFixed(2)}</span>
              ${cancelBtn}
            </div>
          </div>
        `;
        container.insertAdjacentHTML('beforeend', html);
      });
    } catch (err) {
      container.innerHTML = `<p style="color: red; font-size: 1.6rem;">Error loading orders: ${err.message}</p>`;
    }
  }

  window.cancelOrder = async function(id) {
    if (!confirm('Are you sure you want to cancel this order?')) return;
    try {
      await updateOrderStatus(id, 'cancelled');
      loadOrders();
    } catch (err) {
      alert('Failed to cancel order: ' + err.message);
    }
  };

  loadOrders();
});
