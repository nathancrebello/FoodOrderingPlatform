import uvicorn
import os
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from contextlib import asynccontextmanager
from .admin import admin
from .users_app.api import user_router
from .conversations_app.api import conversation_router
from .users_app.models import UserModel
from .settings import logger, SETTINGS, AsyncSessionLocal, DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_FULLNAME
from .utils.security import get_password_hash, login_app, conversation_app
from .middleware.auth_middleware import AuthMiddleware
from .tasks_wrapper_app.api import tasks_router
from .users_app.models import UserModel
from fastapi.staticfiles import StaticFiles
from .voice_agent_app.api import va_router

######################### LIFECYCLE #########################
@asynccontextmanager
async def lifespan(app : FastAPI):
    logger.info("FAST API: Starting the app")
    # Initialize the database and create the default user
    async with AsyncSessionLocal() as session:
        await init_db(session)  # Call init_db with the session
        yield
    logger.info("FAST API: Stopping the app")  # Log stopping the app

config_data = {
    'GOOGLE_CLIENT_ID': SETTINGS.GOOGLE_CLIENT_ID,
    'GOOGLE_CLIENT_SECRET': SETTINGS.GOOGLE_CLIENT_SECRET,
    'GOOGLE_AUTH_URI': "https://accounts.google.com/o/oauth2/auth",
    'GOOGLE_TOKEN_URI': "https://oauth2.googleapis.com/token",
    'GOOGLE_USERINFO_URI': "https://www.googleapis.com/oauth2/v1/userinfo",
    'REDIRECT_URI': SETTINGS.REDIRECT_URI,
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, "media")

# Create directories if they don't exist
os.makedirs(MEDIA_DIR, exist_ok=True)

######################### FAST API #########################
app = FastAPI(lifespan=lifespan)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

######################## MIDDLEWARE ########################
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

# OAuth client setup
oauth = OAuth()

oauth.register(
    name='google',
    client_id=config_data["GOOGLE_CLIENT_ID"],
    client_secret=config_data["GOOGLE_CLIENT_SECRET"],
    authorize_url=config_data["GOOGLE_AUTH_URI"],
    access_token_url=config_data["GOOGLE_TOKEN_URI"],
    redirect_uri=config_data["REDIRECT_URI"],
    client_kwargs={'scope': 'openid profile email'},
)

######################### ADMIN #########################
admin.mount_to(app)

######################### ROUTES #########################
@app.get("/", tags=["health"])
async def health_check():
    return {"status": "ok", "message" : "Voiceagent API Server"}

app.include_router(user_router, prefix=login_app, tags=["users"])
app.include_router(conversation_router, prefix=conversation_app, tags=["conversations"])
# app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])

######################## INIT DB ########################
async def init_db(session: AsyncSession):
    is_admin = True
    is_verified=True
    # Check for existing user by email
    result = await session.execute(select(UserModel).where(UserModel.email == DEFAULT_ADMIN_EMAIL))
    existing_user = result.scalars().first()

    logger.info(f"Existing user: {existing_user}")

    if existing_user is None:
        hashed_password = get_password_hash(DEFAULT_ADMIN_PASSWORD)
        user = UserModel(
            username=DEFAULT_ADMIN_USERNAME,
            email=DEFAULT_ADMIN_EMAIL,
            hashed_password=hashed_password,
            full_name=DEFAULT_ADMIN_FULLNAME,
            is_admin=is_admin,
            is_verified=True
        )
        session.add(user)  # Add the user to the session
        await session.commit()  # Commit the session to save the user
        logger.info(f"Created default admin user: {DEFAULT_ADMIN_EMAIL}")
    else:
        logger.info(f"Default admin user already exists: {DEFAULT_ADMIN_EMAIL}")

########################### RUN APP ###########################
if __name__ == "__main__":
    uvicorn.run(app)
