import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import HTTPException, Depends, status, Header
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import models, database

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
if SECRET_KEY is None:
    raise ValueError("No SECRET_KEY set in environment variables")

if ALGORITHM is None:
    raise ValueError("ALGORITHM must be set and cannot be None")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
        Creates a JWT access token with an expiration time.

        This function generates a JWT (JSON Web Token) for authentication. It takes
        user-specific data and an optional expiration duration. If no expiration is
        provided, the token will expire in one day by default.

        Args:
            data (dict): The payload data to encode in the token.
            expires_delta (Optional[timedelta], optional): The duration after which
                                                          the token expires. Defaults to 1 day.

        Returns:
            str: The encoded JWT access token.

        Example:
            create_access_token({"sub": "user@example.com"})
        """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta if expires_delta else now + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> dict:
    """
    Decodes a JWT token and extracts the payload.

    This function verifies the token's validity and decodes its payload.
    It handles errors like expired or invalid tokens by raising HTTPExceptions.

    Args:
        token (str): The JWT token to decode.

    Returns:
        dict: The decoded payload of the JWT token.

    Raises:
        HTTPException: If the token is expired, invalid, or has an invalid claim.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_current_user(authorization: str = Header(...), db: Session = Depends(database.get_db)) -> models.User:
    """
        Retrieves the current user from the provided JWT token.

        This function extracts and validates the JWT token from the request's
        Authorization header. It then uses the decoded payload to look up
        the corresponding user in the database.

        Args:
            authorization (str): The Authorization header containing the JWT token.
            db (Session): The database session to query the user.

        Returns:
            models.User: The user associated with the provided token.

        Raises:
            HTTPException: If the token is invalid, expired, or if the user is not found.
        """
    try:
        token_prefix, token = authorization.split(" ")
        if token_prefix != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"}
            )

        payload = decode_jwt_token(token)  # Decode and handle errors
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user = db.query(models.User).filter(models.User.email == email).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )

        return user

    except ValueError:  # Handles cases where "Bearer <token>" is missing or malformed
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization header is malformed",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:  # Catch any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
