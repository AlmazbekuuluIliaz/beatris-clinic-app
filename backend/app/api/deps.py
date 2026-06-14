from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import models, repositories
from app.core.database import get_db
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", scheme_name="bearerAuth")


def unauthorized_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Необходимо выполнить вход в систему",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise unauthorized_exception() from exc

    user_id = payload.get("sub")
    if not isinstance(user_id, str):
        raise unauthorized_exception()

    user = repositories.get_user(db, user_id)
    if user is None:
        raise unauthorized_exception()

    return user


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения действия",
        )
    return current_user


def require_doctor(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != models.UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor role is required",
        )
    return current_user
