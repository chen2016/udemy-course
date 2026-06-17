import logging
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from storeapi.conifg import config
from storeapi.database import database, user_table

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"])
credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(email: str, expires_delta: timedelta = None) -> str:
    logger.debug("Creating access token", extra={"email": email})
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=ALGORITHM)


async def get_user(email: str):
    logger.debug("Fetching user from the database", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    result = await database.fetch_one(query)
    if result:
        return result


async def authenticate_user(email: str, password: str):
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    return user


async def get_current_user(token: str):
    try:
        payload = jwt.decode(token, key=config.JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credential_exception
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except JWTError as e:
        raise credential_exception from e
    user = await get_user(email=email)
    if user is None:
        raise credential_exception
    return user
