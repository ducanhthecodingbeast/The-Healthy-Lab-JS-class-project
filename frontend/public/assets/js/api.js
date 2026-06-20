const API_BASE_URL = "http://localhost:8000";

async function apiRequest(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const token = localStorage.getItem("thl_token");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const text = await response.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch (err) {
    data = { message: text };
  }

  if (!response.ok) {
    let errMsg = data.detail || data.message || "API request failed";
    if (typeof errMsg === "object") {
      errMsg = JSON.stringify(errMsg);
    }
    throw new Error(errMsg);
  }
  return data;
}

async function login(email, password) {
  return await apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

async function register(userData) {
  return await apiRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify(userData),
  });
}

async function getProducts(include_disabled = false) {
  const query = include_disabled ? "?include_disabled=true" : "";
  return await apiRequest(`/products${query}`);
}

async function createOrder(orderData) {
  return await apiRequest("/orders", {
    method: "POST",
    body: JSON.stringify(orderData),
  });
}

async function getMyOrders() {
  return await apiRequest("/orders/my");
}

async function getAllOrders() {
  return await apiRequest("/orders");
}

async function getOrder(orderId) {
  return await apiRequest(`/orders/${orderId}`);
}

async function updateOrderStatus(orderId, status) {
  return await apiRequest(`/orders/${orderId}/status`, {
    method: "PUT",
    body: JSON.stringify({ status }),
  });
}

async function getUsers() {
  return await apiRequest("/users");
}

async function getAdminSummary() {
  return await apiRequest("/admin/summary");
}

async function createProduct(productData) {
  return await apiRequest("/products", {
    method: "POST",
    body: JSON.stringify(productData),
  });
}

async function updateProduct(productId, productData) {
  return await apiRequest(`/products/${productId}`, {
    method: "PUT",
    body: JSON.stringify(productData),
  });
}

async function optionalApiRequest(path, options = {}, fallback = null) {
  try {
    return await apiRequest(path, options);
  } catch (err) {
    console.warn(`Optional API unavailable: ${path}`, err.message);
    return fallback;
  }
}

async function getStaffProfiles() {
  return await optionalApiRequest("/staff", {}, null);
}

async function getReservations() {
  return await optionalApiRequest("/reservations", {}, null);
}

async function createReservation(reservationData) {
  return await optionalApiRequest("/reservations", {
    method: "POST",
    body: JSON.stringify(reservationData),
  }, null);
}

async function getQueueEntries() {
  return await optionalApiRequest("/queue", {}, null);
}

async function createQueueEntry(queueData) {
  return await optionalApiRequest("/queue", {
    method: "POST",
    body: JSON.stringify(queueData),
  }, null);
}

async function getInventoryItems() {
  return await optionalApiRequest("/inventory", {}, null);
}

async function getSuppliers() {
  return await optionalApiRequest("/suppliers", {}, null);
}

async function getNotifications() {
  return await optionalApiRequest("/notifications", {}, null);
}

async function getMembership() {
  return await optionalApiRequest("/memberships/me", {}, null);
}

async function getVouchers() {
  return await optionalApiRequest("/vouchers", {}, null);
}

// --- New additions ---
async function getFoodLabOptions() {
  return await optionalApiRequest("/food-lab/options", {}, null);
}

async function previewFoodLabItem(data) {
  return await optionalApiRequest("/food-lab/preview", {
    method: "POST",
    body: JSON.stringify(data),
  }, null);
}

async function getPayments(filters = {}) {
  const query = new URLSearchParams(filters).toString();
  const url = query ? `/payments?${query}` : "/payments";
  return await optionalApiRequest(url, {}, null);
}

async function createPayment(paymentData) {
  return await optionalApiRequest("/payments", {
    method: "POST",
    body: JSON.stringify(paymentData),
  }, null);
}

async function updatePaymentStatus(paymentId, status) {
  return await optionalApiRequest(`/payments/${paymentId}/status`, {
    method: "PUT",
    body: JSON.stringify({ status }),
  }, null);
}

async function getIngredients() {
  return await optionalApiRequest("/ingredients", {}, null);
}

async function createIngredient(data) {
  return await optionalApiRequest("/ingredients", {
    method: "POST",
    body: JSON.stringify(data),
  }, null);
}

async function getRecipes(productId = null) {
  const query = productId ? `?product_id=${productId}` : "";
  return await optionalApiRequest(`/recipes${query}`, {}, null);
}

async function createRecipeItem(data) {
  return await optionalApiRequest("/recipes", {
    method: "POST",
    body: JSON.stringify(data),
  }, null);
}

async function getInventoryLots() {
  return await optionalApiRequest("/inventory/lots", {}, null);
}

async function createInventoryLot(data) {
  return await optionalApiRequest("/inventory/lots", {
    method: "POST",
    body: JSON.stringify(data),
  }, null);
}

async function createSupplier(data) {
  return await optionalApiRequest("/suppliers", {
    method: "POST",
    body: JSON.stringify(data),
  }, null);
}

async function getTables() {
  return await optionalApiRequest("/tables", {}, null);
}

async function createTable(data) {
  return await optionalApiRequest("/tables", {
    method: "POST",
    body: JSON.stringify(data),
  }, null);
}

async function updateReservationStatus(reservationId, status) {
  return await optionalApiRequest(`/reservations/${reservationId}/status`, {
    method: "PUT",
    body: JSON.stringify({ status }),
  }, null);
}

async function completeReservation(reservationId) {
  return await optionalApiRequest(`/reservations/${reservationId}/complete`, {
    method: "POST",
  }, null);
}

async function callNextQueueEntry() {
  return await optionalApiRequest("/queue/next/call", {
    method: "POST",
  }, null);
}

async function seatQueueEntry(entryId) {
  return await optionalApiRequest(`/queue/${entryId}/seat`, {
    method: "POST",
  }, null);
}

async function updateQueueStatus(entryId, data) {
  return await optionalApiRequest(`/queue/${entryId}/status`, {
    method: "PUT",
    body: JSON.stringify(data),
  }, null);
}

async function createStaffProfile(data) {
  return await optionalApiRequest("/staff", {
    method: "POST",
    body: JSON.stringify(data),
  }, null);
}
