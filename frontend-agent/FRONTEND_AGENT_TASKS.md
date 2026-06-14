# Frontend Agent Handoff: The Healthy Lab

This project now has a FastAPI backend. Your task is to connect the existing static HTML/CSS/vanilla JavaScript frontend to that backend.

Do not rewrite the site in React. Keep the current visual style and page structure as much as possible.

## Backend URLs

Use these during local development:

```text
Frontend: http://localhost:5500
Backend API: http://localhost:8000
FastAPI Docs: http://localhost:8000/docs
```

## Auth Data Stored In localStorage

After login/register, store:

```js
// TODO(frontend-agent): Save this object after /auth/login or /auth/register.
{
  token: response.token,
  id: response.id,
  name: response.name,
  email: response.email,
  role: response.role
}
```

Use `Authorization: Bearer <token>` for protected requests.

## Files To Add Or Update

Create or update these frontend files:

```text
assets/js/api.js
assets/js/auth.js
assets/js/cart.js
assets/js/order-history.js
assets/js/chef-dashboard.js
assets/js/delivery-dashboard.js
assets/js/admin-dashboard.js
login.html
register.html
order-history.html
chef-dashboard.html
delivery-dashboard.html
admin-dashboard.html
index.html
food-lab.html
```

## Required JavaScript Helpers

In `assets/js/api.js`, implement:

```js
// TODO(frontend-agent): Keep all fetch calls here.
// - API_BASE_URL = "http://localhost:8000"
// - apiRequest(path, options = {})
// - login(email, password)
// - register(userData)
// - getProducts()
// - createOrder(orderData)
// - getMyOrders()
// - getAllOrders()
// - getOrder(orderId)
// - updateOrderStatus(orderId, status)
// - getUsers()
// - getAdminSummary()
// - createProduct(productData)
// - updateProduct(productId, productData)
```

In `assets/js/auth.js`, implement:

```js
// TODO(frontend-agent): Manage frontend auth state.
// - saveAuth(user)
// - getAuth()
// - logout()
// - getCurrentUser()
// - requireLogin()
// - requireRole(role)
// - renderHeaderAuthState()
```

## Checkout Requirements

Replace fake checkout alerts with `POST /orders`.

Normal menu cart item example:

```js
// TODO(frontend-agent): Send product_id for normal menu items.
{
  product_id: 1,
  quantity: 2,
  custom_details: "Extra avocado"
}
```

Custom Food Lab item example:

```js
// TODO(frontend-agent): Send product_name and unit_price for custom meals.
{
  product_name: "Custom Food Lab Bowl",
  quantity: 1,
  unit_price: 12.5,
  total_price: 12.5,
  custom_details: JSON.stringify({
    base: "brown rice",
    protein: "grilled chicken",
    toppings: ["avocado", "spinach"],
    sauce: "lemon tahini"
  })
}
```

Full checkout request:

```js
// TODO(frontend-agent): Build this from logged-in user + checkout form + localStorage cart.
{
  customer_name: "Customer",
  customer_phone: "0900000004",
  delivery_address: "123 Green Street",
  note: "Please deliver after 6 PM",
  items: [...]
}
```

After successful checkout:

```js
// TODO(frontend-agent):
// - Clear cart localStorage
// - Show order confirmation
// - Link or redirect to order-history.html
```

## Role Pages

Customer:

```js
// TODO(frontend-agent): order-history.html
// - requireRole("customer")
// - GET /orders/my
// - render order cards/table
// - allow cancelling only pending orders with PUT /orders/{id}/status {"status":"cancelled"}
```

Chef:

```js
// TODO(frontend-agent): chef-dashboard.html
// - requireRole("chef")
// - GET /orders
// - show pending/preparing orders
// - pending -> preparing
// - preparing -> ready
// - show custom_details for Food Lab orders
```

Delivery:

```js
// TODO(frontend-agent): delivery-dashboard.html
// - requireRole("delivery")
// - GET /orders
// - show ready/delivering orders
// - ready -> delivering
// - delivering -> delivered
// - show customer name, phone, address, and note
```

Admin:

```js
// TODO(frontend-agent): admin-dashboard.html
// - requireRole("admin")
// - GET /admin/summary
// - GET /orders
// - GET /users
// - GET /products?include_disabled=true
// - POST /products
// - PUT /products/{id}
// - allow changing any order status
// - allow disabling products by setting is_available false
```

## Header Behavior

```js
// TODO(frontend-agent): Update shared header rendering.
// If logged out: show Login and Register.
// If logged in: show name, role, Logout, and dashboard link.
// Dashboard links:
// - customer -> order-history.html
// - chef -> chef-dashboard.html
// - delivery -> delivery-dashboard.html
// - admin -> admin-dashboard.html
```

## Backend Login Accounts

All passwords are:

```text
password123
```

```text
admin@healthylab.test
chef@healthylab.test
delivery@healthylab.test
customer@healthylab.test
```

## Suggested Prompt For The Frontend Agent

```text
You are working on The Healthy Lab frontend. Do not change the FastAPI backend.
Use vanilla JavaScript only. Keep the existing visual style. Connect the existing static
pages to the backend described in frontend-agent/FRONTEND_AGENT_TASKS.md.
Implement API helpers, auth helpers, real cart checkout, customer order history,
chef dashboard, delivery dashboard, admin dashboard, and role-based page protection.
Do not use React, Supabase, payment gateways, maps, email verification, or cloud storage.
```
