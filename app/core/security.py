"""Security utilities for JWT token validation and Clerk integration."""

import json
import time
from typing import Dict, Optional, Any
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
from .config import get_settings

settings = get_settings()

# Security scheme for Bearer tokens
security = HTTPBearer()


class ClerkJWTValidator:
    """Validates Clerk JWT tokens using JWKS."""

    def __init__(self):
        self.jwks_cache: Optional[Dict[str, Any]] = None
        self.jwks_cache_time: float = 0
        self.cache_duration = 3600  # 1 hour cache

    async def get_jwks(self) -> Dict[str, Any]:
        """Fetch JWKS from Clerk with caching."""
        current_time = time.time()

        # Return cached JWKS if still valid
        if (self.jwks_cache and
            current_time - self.jwks_cache_time < self.cache_duration):
            return self.jwks_cache

        try:
            # Fetch JWKS from Clerk
            jwks_url = f"{settings.CLERK_JWT_ISSUER}/.well-known/jwks.json"
            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_url, timeout=10.0)
                response.raise_for_status()

                self.jwks_cache = response.json()
                self.jwks_cache_time = current_time
                return self.jwks_cache

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to fetch JWKS: {str(e)}"
            )

    def get_signing_key(self, jwks: Dict[str, Any], kid: str) -> str:
        """Extract signing key from JWKS for given kid."""
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                # Convert JWK to PEM format for jose
                from jose.utils import base64url_decode
                import base64

                n = base64url_decode(key["n"])
                e = base64url_decode(key["e"])

                # Create RSA public key
                from cryptography.hazmat.primitives.asymmetric import rsa
                from cryptography.hazmat.primitives import serialization

                public_numbers = rsa.RSAPublicNumbers(
                    int.from_bytes(e, 'big'),
                    int.from_bytes(n, 'big')
                )
                public_key = rsa.RSAPublicKey(public_numbers)

                pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
                return pem.decode('utf-8')

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find matching key in JWKS"
        )

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode Clerk JWT token."""
        try:
            # Decode header to get kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing kid in header"
                )

            # Get JWKS and signing key
            jwks = await self.get_jwks()
            signing_key = self.get_signing_key(jwks, kid)

            # Verify and decode token
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                issuer=settings.CLERK_JWT_ISSUER,
                options={"verify_aud": False}  # Clerk doesn't always include aud
            )

            return payload

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}"
            )


# Global JWT validator instance
jwt_validator = ClerkJWTValidator()


async def verify_clerk_token(token: str) -> Dict[str, Any]:
    """Verify Clerk JWT token and return payload."""
    if not settings.CLERK_SECRET_KEY:
        # Development mode - return mock user
        return {
            "sub": "dev_user_123",
            "email": "dev@example.com",
            "first_name": "Dev",
            "last_name": "User"
        }

    return await jwt_validator.verify_token(token)


def extract_user_id(payload: Dict[str, Any]) -> str:
    """Extract user ID from JWT payload."""
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID"
        )
    return user_id


def extract_user_email(payload: Dict[str, Any]) -> Optional[str]:
    """Extract user email from JWT payload."""
    return payload.get("email")


def extract_user_metadata(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract user metadata from JWT payload."""
    return {
        "user_id": extract_user_id(payload),
        "email": extract_user_email(payload),
        "first_name": payload.get("first_name"),
        "last_name": payload.get("last_name"),
        "username": payload.get("username"),
        "image_url": payload.get("image_url"),
        "created_at": payload.get("iat"),
        "updated_at": payload.get("updated_at")
    }