/**
 * js/register.js
 * ---------------
 * Handles the registration form: submits the new account to
 * POST /auth/register, then sends the person to the login page.
 */

const form = document.getElementById("register-form");
const errorAlert = document.getElementById("error-alert");
const successAlert = document.getElementById("success-alert");
const submitBtn = document.getElementById("submit-btn");

if (auth.isLoggedIn()) {
  window.location.href = "dashboard.html";
}

function showError(message) {
  successAlert.hidden = true;
  errorAlert.textContent = message;
  errorAlert.hidden = false;
}

function showSuccess(message) {
  errorAlert.hidden = true;
  successAlert.textContent = message;
  successAlert.hidden = false;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorAlert.hidden = true;
  successAlert.hidden = true;

  const full_name = document.getElementById("full_name").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const role = document.getElementById("role").value;

  submitBtn.disabled = true;
  submitBtn.textContent = "Creating account…";

  try {
    await apiRequest("/auth/register", {
      method: "POST",
      body: { full_name, email, password, role },
    });

    showSuccess("Account created. Redirecting to login…");
    setTimeout(() => {
      window.location.href = "index.html";
    }, 1200);
  } catch (err) {
    showError(err.message);
    submitBtn.disabled = false;
    submitBtn.textContent = "Create account";
  }
});
