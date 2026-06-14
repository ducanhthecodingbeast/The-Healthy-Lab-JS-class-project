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
