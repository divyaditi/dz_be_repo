import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from settings import settings

bearer_scheme = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    """
    FastAPI dependency that validates the Bearer token from the Authorization header.

    Raises:
        401 - Token expired
        401 - Invalid token
    Returns:
        The decoded user_email from the token payload.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload.get("user_email")

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail={
                "error_code": "TOKEN_EXPIRED",
                "message": "Token has expired. Please log in again.",
            },
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail={
                "error_code": "INVALID_TOKEN",
                "message": "Invalid token. Authentication failed.",
            },
        )
