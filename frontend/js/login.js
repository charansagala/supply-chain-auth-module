/**
 * js/login.js
 * -----------
 * Handles the login form: submits credentials to POST /auth/login,
 * stores the JWT + user info on success, and redirects to the dashboard.
 */

const form = document.getElementById("login-form");
const errorAlert = document.getElementById("error-alert");
const submitBtn = document.getElementById("submit-btn");
const statusApi = document.getElementById("status-api");

// If we already have a valid-looking session, skip straight to the dashboard.
if (auth.isLoggedIn()) {
  window.location.href = "dashboard.html";
}

// Quick, non-blocking check that the backend is reachable, just to show
// a friendlier status message on the right-hand panel.
apiRequest("/")
  .then(() => {
    statusApi.textContent = "connected";
  })
  .catch(() => {
    statusApi.textContent = "unreachable — start the FastAPI server";
  });

function showError(message) {
  errorAlert.textContent = message;
  errorAlert.hidden = false;
}

function hideError() {
  errorAlert.hidden = true;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  submitBtn.disabled = true;
  submitBtn.textContent = "Logging in…";

  try {
    const data = await apiRequest("/auth/login", {
      method: "POST",
      body: { email, password },
    });

    auth.saveSession(data.access_token, data.user);
    window.location.href = "dashboard.html";
  } catch (err) {
    showError(err.message);
    submitBtn.disabled = false;
    submitBtn.textContent = "Log in";
  }
});
