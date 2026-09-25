/**
 * js/dashboard.js
 * ----------------
 * Drives the dashboard page:
 *   1. Confirms the user is logged in (redirects to login if not).
 *   2. Loads the fresh profile from GET /auth/me.
 *   3. Shows role-appropriate content (manager/planner dashboard data).
 *   4. If the user is an ADMIN, loads GET /users and lets them change
 *      roles (PUT /users/{id}/role) or delete users (DELETE /users/{id}).
 */

const dashboardError = document.getElementById("dashboard-error");

function showDashboardError(message) {
  dashboardError.textContent = message;
  dashboardError.hidden = false;
}

function formatDate(isoString) {
  const d = new Date(isoString);
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

// --- Guard: bounce to login if there's no session at all -------------------
if (!auth.isLoggedIn()) {
  window.location.href = "index.html";
}

let currentUser = null;

async function init() {
  // Always re-fetch the profile rather than trusting the cached copy,
  // in case the user's role was changed by an admin since they logged in.
  try {
    currentUser = await apiRequest("/auth/me", { auth: true });
  } catch (err) {
    // Token missing/expired/invalid -> send back to login.
    auth.clearSession();
    window.location.href = "index.html";
    return;
  }

  renderTopbar(currentUser);
  renderProfile(currentUser);
  renderRoleSection(currentUser);

  if (currentUser.role === "ADMIN") {
    document.getElementById("admin-section").hidden = false;
    loadUsersTable();
  }
}

function renderTopbar(user) {
  document.getElementById("topbar-name").textContent = user.full_name;
  const roleBadge = document.getElementById("topbar-role");
  roleBadge.textContent = user.role;
  roleBadge.dataset.role = user.role;
}

function renderProfile(user) {
  const container = document.getElementById("profile-stats");
  container.innerHTML = "";

  const stats = [
    { label: "Name", value: user.full_name },
    { label: "Email", value: user.email },
    { label: "Role", value: user.role },
    { label: "Account created", value: formatDate(user.created_at) },
  ];

  for (const stat of stats) {
    const div = document.createElement("div");
    div.className = "stat";
    div.innerHTML = `<div class="stat__label">${stat.label}</div><div class="stat__value">${stat.value}</div>`;
    container.appendChild(div);
  }
}

// Static, role-specific feature descriptions. Admin sees a summary of full
// system access; manager/planner mirror what their live dashboard endpoint
// currently reports (those endpoints will return real data once the
// Forecasting, Inventory, and Analytics modules are built).
const ROLE_CONTENT = {
  ADMIN: {
    title: "Administration",
    hint: "Full system access",
    features: [
      "Create, view, update, and deactivate any user",
      "Assign or change roles for any account",
      "Access every module as it comes online",
      "Oversee manager and planner dashboards",
    ],
  },
  MANAGER: {
    title: "Manager dashboard",
    hint: "Read access to forecasting and analytics",
    features: [
      "View demand forecasts",
      "View analytics dashboards",
      "View inventory information",
      "View procurement recommendations",
      "Monitor forecast anomalies",
    ],
  },
  PLANNER: {
    title: "Planner dashboard",
    hint: "Read access to operational data",
    features: [
      "View demand forecasts",
      "View inventory information",
      "View procurement recommendations",
      "View inventory alerts",
    ],
  },
};

async function renderRoleSection(user) {
  const content = ROLE_CONTENT[user.role];
  if (!content) return;

  document.getElementById("role-section-title").textContent = content.title;
  document.getElementById("role-section-hint").textContent = content.hint;

  const list = document.getElementById("role-feature-list");
  list.innerHTML = "";
  for (const feature of content.features) {
    const li = document.createElement("li");
    li.textContent = feature;
    list.appendChild(li);
  }

  document.getElementById("role-section").hidden = false;

  // Also ping the matching protected endpoint, purely to prove the
  // role-based route guard is actually working end to end (not just UI).
  const endpoint = user.role === "MANAGER" ? "/manager/dashboard"
    : user.role === "PLANNER" ? "/planner/dashboard"
    : null;

  if (endpoint) {
    try {
      await apiRequest(endpoint, { auth: true });
    } catch (err) {
      showDashboardError(`Could not load ${endpoint}: ${err.message}`);
    }
  }
}

// --- Admin: user management table ------------------------------------------

async function loadUsersTable() {
  const tbody = document.getElementById("users-table-body");

  try {
    const users = await apiRequest("/users", { auth: true });

    if (users.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="empty-state">No users found.</td></tr>`;
      return;
    }

    tbody.innerHTML = "";
    for (const user of users) {
      tbody.appendChild(buildUserRow(user));
    }
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-state">Couldn't load users: ${err.message}</td></tr>`;
  }
}

function buildUserRow(user) {
  const tr = document.createElement("tr");

  const isSelf = currentUser && user.id === currentUser.id;

  tr.innerHTML = `
    <td>${user.full_name}</td>
    <td>${user.email}</td>
    <td class="mono">${user.role}</td>
    <td><span class="status-pill ${user.is_active ? "status-pill--active" : "status-pill--inactive"}">${user.is_active ? "active" : "inactive"}</span></td>
    <td class="mono">${formatDate(user.created_at)}</td>
    <td class="table-actions">
      <select class="role-select" ${isSelf ? "disabled" : ""}>
        <option value="ADMIN" ${user.role === "ADMIN" ? "selected" : ""}>ADMIN</option>
        <option value="MANAGER" ${user.role === "MANAGER" ? "selected" : ""}>MANAGER</option>
        <option value="PLANNER" ${user.role === "PLANNER" ? "selected" : ""}>PLANNER</option>
      </select>
      <button class="btn btn--ghost btn--small delete-btn" ${isSelf ? "disabled title='You cannot delete your own account'" : ""}>Delete</button>
    </td>
  `;

  const roleSelect = tr.querySelector(".role-select");
  roleSelect.addEventListener("change", async () => {
    const newRole = roleSelect.value;
    try {
      await apiRequest(`/users/${user.id}/role`, {
        method: "PUT",
        auth: true,
        body: { role: newRole },
      });
    } catch (err) {
      showDashboardError(`Couldn't update role: ${err.message}`);
      roleSelect.value = user.role; // revert the dropdown on failure
    }
  });

  const deleteBtn = tr.querySelector(".delete-btn");
  deleteBtn.addEventListener("click", async () => {
    if (!confirm(`Delete ${user.full_name}? This can't be undone.`)) return;
    try {
      await apiRequest(`/users/${user.id}`, { method: "DELETE", auth: true });
      tr.remove();
    } catch (err) {
      showDashboardError(`Couldn't delete user: ${err.message}`);
    }
  });

  return tr;
}

// --- Logout ------------------------------------------------------------

document.getElementById("logout-btn").addEventListener("click", () => {
  auth.clearSession();
  window.location.href = "index.html";
});

init();
