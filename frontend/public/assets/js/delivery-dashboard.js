document.addEventListener('DOMContentLoaded', () => {
  if (!requireRole('delivery')) return;

  const container = document.getElementById('orders-container');

  async function loadOrders() {
    try {
      const allOrders = await getAllOrders();
      // Delivery sees ready and delivering orders
      const orders = allOrders.filter(o => o.status === 'ready' || o.status === 'delivering');
      
      if (orders.length === 0) {
        container.innerHTML = '<p style="font-size: 1.6rem; color: #666;">No orders ready for delivery.</p>';
        return;
      }

      container.innerHTML = '';
      orders.forEach(order => {
        let actionBtn = '';
        if (order.status === 'ready') {
          actionBtn = `<button class="action-btn" onclick="updateStatus(${order.id}, 'delivering')">Start Delivery</button>`;
        } else if (order.status === 'delivering') {
          actionBtn = `<button class="action-btn delivered" onclick="updateStatus(${order.id}, 'delivered')">Mark Delivered</button>`;
        }

        const html = `
          <div class="order-card ${order.status}">
            <div class="order-header">
              <span style="font-size: 1.8rem; font-weight: bold;">Order #${order.id}</span>
              <span class="status-badge status-${order.status}">${order.status}</span>
            </div>
            <div class="delivery-info">
              <p><strong>Customer:</strong> ${order.customer_name}</p>
              <p><strong>Phone:</strong> ${order.customer_phone || 'N/A'}</p>
              <p><strong>Address:</strong> ${order.delivery_address}</p>
              ${order.note ? `<p><strong>Note:</strong> ${order.note}</p>` : ''}
            </div>
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
