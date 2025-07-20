from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import starlette.status as status_code
import jwt
from sqlalchemy.future import select
from app.users_app.schemas import AnonymousUserSchema, UserSchema
from app.users_app.models import UserModel
from app.utils.security import login_url
from app.settings import SETTINGS, logger, AsyncSessionLocal


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        authorization: str = request.headers.get('Authorization')
        logger.info(f"Authorization: {authorization}")
        logger.info(f"Request: {request.url.path}")

        # Special case for the login path
        if request.url.path == login_url:
            request.state.user = AnonymousUserSchema()
            request.state.is_authenticated = False
            response = await call_next(request)
            return response

        if authorization:
            logger.info(f"Authorization: {authorization}")
            try:
                scheme, token = authorization.split()
                if scheme.lower() != 'bearer':
                    return JSONResponse(
                        status_code=status_code.HTTP_401_UNAUTHORIZED,
                        content="Invalid Authorization header",
                        headers={"WWW-Authenticate": "Bearer"}
                    )

                payload = jwt.decode(
                    token, SETTINGS.SECRET_KEY.get_secret_value(), algorithms=[SETTINGS.ALGORITHM])
                user_id = int(payload.get("sub"))

                if user_id is None:
                    return JSONResponse(
                        status_code=status_code.HTTP_401_UNAUTHORIZED,
                        content="Invalid token",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                    
                logger.info(f"User ID: {user_id}")
                    
                async with AsyncSessionLocal() as session:
                    result = await session.execute(select(UserModel).where(UserModel.id == user_id))
                    user = result.scalars().first()
                    await session.commit()

                logger.info(f"User: {user.username}")
                if user is None or user.token != token:
                    logger.info(f"Invalid token {user.token != token}")
                    return JSONResponse(
                        status_code=status_code.HTTP_401_UNAUTHORIZED,
                        content="Invalid token",
                        headers={"WWW-Authenticate": "Bearer"}
                    )

                request.state.user = UserSchema.model_validate(user, from_attributes=True)
                request.state.is_authenticated = True

            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError) as e:
                logger.error(f"Error: {e}")
                return JSONResponse(
                    status_code=status_code.HTTP_401_UNAUTHORIZED,
                    content="Invalid or expiredtoken",
                    headers={"WWW-Authenticate": "Bearer"}
                )

        else:
            logger.info("Authentication token not found")
            request.state.user = AnonymousUserSchema()  # Return anonymous user
            request.state.is_authenticated = False

        response = await call_next(request)
        return response
