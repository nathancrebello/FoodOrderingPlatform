from fastapi import APIRouter, HTTPException, Request, Depends
import starlette.status as status_code
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import jwt
from app.utils.db_base import get_db
from .schemas import AnonymousUserSchema, UserSchema, RegisterUserSchema, TokenSchema, VerifyUserSchema
from .models import UserModel
from app.utils.exceptions import InvalidCredentialsException
from app.settings import logger, SETTINGS
from app.utils.security import (
    get_password_hash,
    authenticate_user,
    create_token_for_user,
    create_email_verification_token,
    generate_verification_code,
    store_verification_token_for_user,
    get_verification_token_for_user,
    oauth2_scheme,
    login_path,
    check_if_admin
)
from .tasks import send_verification_email

user_router = APIRouter()

@user_router.post("/register")
async def register_user(user: RegisterUserSchema, session: AsyncSession = Depends(get_db)):
    # Check if the user already exists
    existing_user = await session.execute(select(UserModel).where(UserModel.email == user.email))
    if existing_user.scalars().first():
        raise HTTPException(
            status_code=status_code.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Generate a random verification code
    verification_code = generate_verification_code()

    # Create new user but don't verify yet
    new_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password.get_secret_value()),
        full_name=user.full_name,
        is_admin=user.is_admin or False,
        is_verified=False  # Initially unverified
    )

    session.add(new_user)
    await session.commit()

    # Create a JWT token with the email and verification code
    verification_token = create_email_verification_token(
        user.email, verification_code)

    # Store the token with redis
    store_verification_token_for_user(user.email, verification_token)

    # Send the verification code in the email
    send_verification_email.delay(user.email, verification_code)

    return {"msg": "Please check your email for the verification code."}


@user_router.post("/verify")
async def verify_user(verify_user: VerifyUserSchema, session: AsyncSession = Depends(get_db)):
    email = verify_user.email
    code = verify_user.code
    result = await session.execute(select(UserModel).where(UserModel.email == email))
    user = result.scalars().first()

    if user is None:
        raise HTTPException(
            status_code=status_code.HTTP_404_NOT_FOUND, detail="User not found")

    if user.is_verified:
        raise HTTPException(
            status_code=status_code.HTTP_400_BAD_REQUEST, detail="User is already verified")

    # Retrieve the JWT token for verification
    token = get_verification_token_for_user(email)

    try:
        payload = jwt.decode(token, SETTINGS.SECRET_KEY.get_secret_value(),
                             algorithms=[SETTINGS.ALGORITHM])
        token_email: str = payload.get("sub")
        token_code: int = int(payload.get("code"))

        if token_email is None or token_code is None:
            raise HTTPException(
                status_code=status_code.HTTP_400_BAD_REQUEST, detail="Invalid token")
    except:
        raise HTTPException(
            status_code=status_code.HTTP_400_BAD_REQUEST, detail="Invalid token")

    if token_code != code:
        raise HTTPException(
            status_code=status_code.HTTP_400_BAD_REQUEST, detail="Invalid verification code")

    # Verify user and mark them as verified
    user.is_verified = True
    session.add(user)
    await session.commit()

    return {"msg": "User verified successfully"}


@user_router.post(login_path, response_model=TokenSchema)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_db)):
    user = await authenticate_user(session, form_data.username, form_data.password)

    if user is None:
        raise InvalidCredentialsException()

    user = await create_token_for_user(session, user)
    
    await session.commit()

    return TokenSchema(access_token=user.token, token_type="bearer")


@user_router.get("/me", response_model=UserSchema | AnonymousUserSchema)
async def whoami(request: Request):
    user = request.state.user
    logger.info(f"Type of User: {type(user).__name__}")
    return user


@user_router.get("/users", response_model=list[UserSchema], dependencies=[Depends(check_if_admin)])
async def list_users(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(UserModel))
    users = result.scalars().all()
    return users
