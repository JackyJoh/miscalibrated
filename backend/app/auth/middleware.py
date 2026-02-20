"""
app/auth/middleware.py — Auth0 JWT validation for FastAPI.

HOW AUTH0 JWT VALIDATION WORKS (plain English):
─────────────────────────────────────────────────
1. The user logs in via Auth0 in the React app (Auth0 SDK handles this).
2. Auth0 returns an "access token" — a JWT (JSON Web Token). A JWT is a
   base64-encoded string with three parts: header.payload.signature
3. The React app sends this token in every API request as a header:
      Authorization: Bearer <token>
4. This middleware intercepts every protected request, extracts the token,
   and verifies it:
   a. Fetches Auth0's public signing keys from their JWKS endpoint.
      (JWKS = JSON Web Key Set — Auth0 publishes the public half of the
      RSA keypair they used to sign the token.)
   b. Verifies the token's RSA signature using those keys.
   c. Checks that the token hasn't expired.
   d. Checks that the "audience" claim matches our API (prevents a token
      meant for another service from being accepted here).
5. If verification passes, we extract the user's Auth0 ID from the token
   (the "sub" claim, e.g. "auth0|abc123") and make it available to routes.
6. If anything fails, we return a 401 Unauthorized response immediately.
"""

import httpx
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

# HTTPBearer extracts the "Bearer <token>" string from the Authorization header
bearer_scheme = HTTPBearer()

# Cache the JWKS (public keys) so we don't fetch them on every request.
# In production, add a proper TTL cache (e.g. with cachetools).
_jwks_cache: dict | None = None


async def get_jwks() -> dict:
    """
    Fetch Auth0's public signing keys.

    Auth0 uses RS256: they sign JWTs with a private key and publish the
    matching public key at a well-known URL. We use the public key to verify
    that a token was actually signed by Auth0 and wasn't tampered with.
    """
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.auth0_jwks_uri)
            response.raise_for_status()
            _jwks_cache = response.json()
    return _jwks_cache


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> dict:
    """
    FastAPI dependency that validates an Auth0 JWT.

    Usage in a route:
        @router.get("/protected")
        async def protected(user: dict = Depends(verify_token)):
            user_id = user["sub"]  # Auth0 user ID, e.g. "auth0|abc123"

    Raises 401 if the token is missing, expired, or invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        # Fetch Auth0's public keys
        jwks = await get_jwks()

        # Decode and verify the JWT.
        # python-jose automatically:
        #   - Picks the right key from JWKS using the token's "kid" header
        #   - Verifies the RSA signature
        #   - Checks expiry, audience, and issuer claims
        payload = jwt.decode(
            token,
            jwks,
            algorithms=settings.auth0_algorithms,
            audience=settings.auth0_audience,
            issuer=settings.auth0_issuer,
        )
        return payload  # Contains "sub" (user ID), "email", scopes, etc.

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception


def get_current_user_id(token_payload: dict = Depends(verify_token)) -> str:
    """
    Convenience dependency that returns just the Auth0 user ID (the 'sub' claim).

    Usage in a route:
        @router.get("/me")
        async def get_me(user_id: str = Depends(get_current_user_id)):
            ...
    """
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token.")
    return user_id
