/**
 * main.jsx — React application entry point.
 *
 * Wraps the app in Auth0Provider so every component in the tree can access
 * Auth0 state (isAuthenticated, user, getAccessTokenSilently, etc.) via hooks.
 *
 * HOW AUTH0 WORKS IN REACT (plain English):
 * ──────────────────────────────────────────
 * 1. Auth0Provider initializes the Auth0 SDK with your tenant config.
 * 2. When the user clicks "Log In", we call loginWithRedirect() — Auth0
 *    takes them to the Auth0 login page (hosted by Auth0, not us).
 * 3. After login, Auth0 redirects back to your app with an authorization code.
 * 4. The SDK exchanges that code for an access token (JWT) silently.
 * 5. When making API calls, we call getAccessTokenSilently() to get the current
 *    JWT, then attach it as "Authorization: Bearer <token>" on requests.
 * 6. The FastAPI backend validates that JWT (checks Auth0's signature).
 */

import React from "react";
import ReactDOM from "react-dom/client";
import { Auth0Provider } from "@auth0/auth0-react";
import App from "./App.jsx";
import "./index.css";

// Auth0 config — these come from your Auth0 Application dashboard.
// In production, inject these via environment variables (Vite exposes
// VITE_* prefixed vars to the browser bundle).
const AUTH0_DOMAIN   = import.meta.env.VITE_AUTH0_DOMAIN   || "your-tenant.us.auth0.com";
const AUTH0_CLIENT_ID = import.meta.env.VITE_AUTH0_CLIENT_ID || "your-client-id";
const AUTH0_AUDIENCE  = import.meta.env.VITE_AUTH0_AUDIENCE  || "https://api.miscalibrated.com";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Auth0Provider
      domain={AUTH0_DOMAIN}
      clientId={AUTH0_CLIENT_ID}
      authorizationParams={{
        redirect_uri: window.location.origin,  // Where Auth0 redirects after login
        audience: AUTH0_AUDIENCE,              // Tells Auth0 to include API scopes in the JWT
      }}
    >
      <App />
    </Auth0Provider>
  </React.StrictMode>
);
