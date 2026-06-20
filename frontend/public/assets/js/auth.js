function saveAuth(authData) {
  localStorage.setItem("thl_token", authData.token);
  localStorage.setItem("thl_user", JSON.stringify({
    id: authData.id,
    name: authData.name,
    email: authData.email,
    role: authData.role,
    phone: authData.phone || '',
    address: authData.address || ''
  }));
}

function getAuth() {
  const user = localStorage.getItem("thl_user");
  const token = localStorage.getItem("thl_token");
  if (!user || !token) return null;
  try {
    return { token, user: JSON.parse(user) };
  } catch (err) {
    return null;
  }
}

function logout() {
  localStorage.removeItem("thl_token");
  localStorage.removeItem("thl_user");
  window.location.href = "index.html";
}

function getCurrentUser() {
  const auth = getAuth();
  return auth ? auth.user : null;
}

function requireLogin() {
  const user = getCurrentUser();
  if (!user) {
    window.location.href = "login.html";
    return false;
  }
  return true;
}

function requireRole(role) {
  if (!requireLogin()) return false;
  const user = getCurrentUser();
  if (user.role !== role && user.role !== 'admin') { // Admin can access everything ideally, or strictly exact role
    if (user.role !== role) {
      alert("Access Denied.");
      window.location.href = "index.html";
      return false;
    }
  }
  return true;
}

function renderHeaderAuthState() {
  const user = getCurrentUser();
  const navbarList = document.querySelector(".navbar-list");
  const btnGroup = document.querySelector(".header-btn-group");

  if (!navbarList || !btnGroup) return;

  // Clear previous auth links
  document.querySelectorAll(".auth-link").forEach((el) => el.remove());

  if (user) {
    let dashboardLink = "index.html";
    if (user.role === "customer") dashboardLink = "order-history.html";
    if (user.role === "chef") dashboardLink = "chef-dashboard.html";
    if (user.role === "delivery") dashboardLink = "delivery-dashboard.html";
    if (user.role === "cashier") dashboardLink = "cashier-dashboard.html";
    if (user.role === "staff") dashboardLink = "staff-dashboard.html";
    if (user.role === "admin") dashboardLink = "admin-dashboard.html";

    const dashHtml = `
      <li class="nav-item auth-link">
        <a href="${dashboardLink}" class="navbar-link" data-nav-link>Dashboard (${user.role})</a>
      </li>
      <li class="nav-item auth-link">
        <a href="reservations.html" class="navbar-link" data-nav-link>Reservations</a>
      </li>
    `;
    navbarList.insertAdjacentHTML("beforeend", dashHtml);

    const userBtnHtml = `
      <div class="auth-link" style="display:flex; align-items:center; gap: 16px;">
        <span style="font-family:var(--ff-rubik, 'Inter', sans-serif); font-weight:500; font-size:1.4rem; text-transform:uppercase; letter-spacing:1px; color:inherit; white-space:nowrap;">${user.name}</span>
        <button onclick="logout()" class="header-btn-outline">Logout</button>
      </div>
    `;
    btnGroup.insertAdjacentHTML("afterbegin", userBtnHtml);
  } else {
    const authHtml = `
      <li class="nav-item auth-link">
        <a href="login.html" class="navbar-link" data-nav-link>Login</a>
      </li>
      <li class="nav-item auth-link">
        <a href="register.html" class="navbar-link" data-nav-link>Register</a>
      </li>
    `;
    navbarList.insertAdjacentHTML("beforeend", authHtml);
  }
}

document.addEventListener("DOMContentLoaded", renderHeaderAuthState);
