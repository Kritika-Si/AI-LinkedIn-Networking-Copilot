
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, RevokedToken
from security import decode_access_token


def get_current_user(
    session_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Please log in.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not session_token:
        raise credentials_error

    payload = decode_access_token(session_token)

    if payload is None:
        raise credentials_error

    user_id = payload.get("sub")
    token_id = payload.get("jti")

    if not user_id or not token_id:
        raise credentials_error

    # Check whether this JWT has been revoked.
    revoked_token = (
        db.query(RevokedToken)
        .filter(RevokedToken.jti == token_id)
        .first()
    )

    if revoked_token is not None:
        raise credentials_error

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise credentials_error

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise credentials_error

    return user
