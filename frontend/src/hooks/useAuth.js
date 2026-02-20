/**
 * hooks/useAuth.js — Convenience wrapper around Auth0's useAuth0 hook.
 *
 * Provides getAuthHeader() — the key utility for making authenticated API calls.
 * Every request to the FastAPI backend must include the JWT in the Authorization header.
 *
 * Usage:
 *   const { getAuthHeader } = useAuth();
 *   const response = await api.get("/markets", { headers: await getAuthHeader() });
 */

import { useAuth0 } from "@auth0/auth0-react";

export function useAuth() {
  const {
    isAuthenticated,
    isLoading,
    user,
    loginWithRedirect,
    logout,
    getAccessTokenSilently,
  } = useAuth0();

  /**
   * Returns an Authorization header object with a fresh JWT.
   *
   * getAccessTokenSilently() checks if the current token is still valid.
   * If it's expired, it silently refreshes it using the refresh token
   * (or via an invisible iframe — Auth0 handles this for you).
   *
   * You never need to manually store or refresh the token — just call this
   * before each API request and Auth0 takes care of the rest.
   */
  const getAuthHeader = async () => {
    const token = await getAccessTokenSilently();
    return { Authorization: `Bearer ${token}` };
  };

  return {
    isAuthenticated,
    isLoading,
    user,
    loginWithRedirect,
    logout,
    getAuthHeader,
  };
}
