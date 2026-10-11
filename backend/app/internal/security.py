from datetime import datetime, timedelta, UTC

from pwdlib import PasswordHash

import jwt

from app.config import get_settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash a password
    :param password: raw password
    :return: hashed password
    """
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """
    Verify if the raw password match the hashed password
    :param password: raw password
    :param hashed: hashed password
    :return: True or False
    """
    return password_hash.verify(password, hashed)

def create_access_token(subject: str) -> str:
    """
    Create and encode a personal user access token
    :param subject: username
    :return: encoded jwt
    """
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(
        {'sub': subject, 'exp': expire},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

def decode_access_token(token: str) -> str | None:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.InvalidTokenError:
        return None
    return payload.get('sub')
