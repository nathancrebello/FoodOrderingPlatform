from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import starlette.status as status_code
from datetime import datetime, timedelta, timezone
import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request, Depends, HTTPException
from typing import Optional
from datetime import datetime, timedelta
import secrets
from app.settings import async_engine
from app.users_app.models import UserModel
from app.settings import SETTINGS, redis_client
from app.users_app.schemas import UserSchema
from app.utils.db_base import get_db

login_app = "/auth"
login_path = "/login"
conversation_app = "/conversations"
login_url = login_app + login_path
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=login_url)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Return user if exists otherwise return None


async def authenticate_user(session: AsyncSession, username: str, password: str) -> Optional[UserModel]:
    user = await get_user_from_username(session, username)
    if user is None:
        return None
    if not pwd_context.verify(password, user.hashed_password):
        return None
    return user


async def get_user_from_username(session: AsyncSession, username: str) -> Optional[UserModel]:
    result = await session.execute(select(UserModel).where(UserModel.username == username))
    user = result.scalars().first()
    return user

# Create a new JWT token with the expiration time and add it to the user model


async def create_token_for_user(session: AsyncSession, user: UserModel) -> UserModel:
    token_content = str(user.id)
    expiration = datetime.now(
        tz=timezone.utc) + timedelta(minutes=SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"sub": token_content, "exp": expiration},
                       SETTINGS.SECRET_KEY.get_secret_value(), algorithm=SETTINGS.ALGORITHM)

    # Store the token in the database
    user.token = token

    return user


async def check_if_admin(request: Request):
    if not request.state.user.is_admin:
        raise HTTPException(
            status_code=status_code.HTTP_401_UNAUTHORIZED, detail="User is not an admin.")

# JWT token generation for email verification


def create_email_verification_token(email: str, verification_code: str):
    expire = datetime.now() + timedelta(minutes=10)
    to_encode = {"sub": email, "code": verification_code, "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode, SETTINGS.SECRET_KEY.get_secret_value(), algorithm=SETTINGS.ALGORITHM)
    return encoded_jwt

# Generate a random verification code


def generate_verification_code(length: int = 6) -> str:
    """Generate a random numeric verification code with the given length."""
    return ''.join(secrets.choice("0123456789") for _ in range(length))

# Store the token with the email as the key


def store_verification_token_for_user(email: str, token: str, expire_time: int = 600):
    # Set token with expiration (10 minutes)
    redis_client.setex(email, expire_time, token)

# Retrieve the token by email


def get_verification_token_for_user(email: str) -> str:
    token = redis_client.get(email)
    if not token:
        raise HTTPException(status_code=status_code.HTTP_404_NOT_FOUND,
                            detail="Verification token not found")
    # Redis returns byte string, decode to normal string
    return token.decode("utf-8")


# Check if the user is authenticated
def check_if_authenticated(request: Request):
    if not request.state.is_authenticated:
        raise HTTPException(
            status_code=status_code.HTTP_401_UNAUTHORIZED, detail="User is not authenticated.")
