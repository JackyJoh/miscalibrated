/**
 * lib/api.js — Centralized Axios instance for all API calls.
 *
 * Usage:
 *   import api from "@/lib/api";
 *   const { getAuthHeader } = useAuth();
 *
 *   const markets = await api.get("/markets", {
 *     headers: await getAuthHeader(),
 *   });
 *
 * The baseURL is set to /api/v1 — during local dev, Vite proxies /api/* to
 * localhost:8000 (configured in vite.config.js). In production, the same
 * path is served directly by the FastAPI backend.
 */

import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1",
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ── Response interceptor ──────────────────────────────────────────────────
// Centralized error handling. Logs API errors in development.
// TODO: Add toast notifications for user-visible errors.
api.interceptors.response.use(
  (response) => response.data,    // Unwrap axios response — return data directly
  (error) => {
    if (import.meta.env.DEV) {
      console.error("[API Error]", error.response?.status, error.response?.data);
    }
    return Promise.reject(error);
  }
);

export default api;

// ── Typed API helpers (add as routes are built out) ──────────────────────

/** Fetch paginated markets. */
export const fetchMarkets = (params, headers) =>
  api.get("/markets", { params, headers });

/** Fetch edge detections above a given magnitude. */
export const fetchEdges = (params, headers) =>
  api.get("/edges", { params, headers });

/** Get current user's alert preferences. */
export const fetchAlertPreferences = (headers) =>
  api.get("/alerts/preferences", { headers });

/** Update alert preferences. */
export const updateAlertPreferences = (data, headers) =>
  api.patch("/alerts/preferences", data, { headers });
