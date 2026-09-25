/**
 * js/api.js
 * ---------
 * Small shared helper for talking to the FastAPI backend and for
 * storing/reading the JWT in the browser. Every page includes this file
 * before its own page-specific script.
 */

// Change this if your FastAPI server runs somewhere other than localhost:8000
const API_BASE_URL = "http://127.0.0.1:8000";

const TOKEN_KEY = "scfs_access_token";

const auth = {
  saveSession(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem("scfs_user", JSON.stringify(user));
  },
  getToken() {
    return localStorage.getItem(TOKEN_KEY);
  },
  getUser() {
    const raw = localStorage.getItem("scfs_user");
    return raw ? JSON.parse(raw) : null;
  },
  clearSession() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem("scfs_user");
  },
  isLoggedIn() {
    return Boolean(this.getToken());
  },
};

/**
 * Wrapper around fetch() that:
 *  - prefixes the API base URL
 *  - attaches the JWT (if we have one) as a Bearer token
 *  - parses JSON responses
 *  - throws a readable Error with the backend's error message on failure
 */
async function apiRequest(path, { method = "GET", body = null, auth: needsAuth = false } = {}) {
  const headers = { "Content-Type": "application/json" };

  if (needsAuth) {
    const token = auth.getToken();
    if (!token) {
      throw new Error("You're not logged in. Please log in again.");
    }
    headers["Authorization"] = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (networkErr) {
    throw new Error(
      "Could not reach the backend. Is the FastAPI server running at " +
        API_BASE_URL +
        "?"
    );
  }

  // 204 No Content has no body to parse (used by DELETE /users/{id})
  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const message =
      (data && (data.detail || data.message)) ||
      `Request failed with status ${response.status}`;
    // A 401 on an authenticated request usually means the token expired.
    if (response.status === 401 && needsAuth) {
      auth.clearSession();
    }
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }

  return data;
}
