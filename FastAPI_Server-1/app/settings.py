from typing import Optional
import os
import logging
from pydantic import Field
from pydantic.types import SecretStr
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import redis

#################################### ENV VARAIBLES #####################################


class _Settings(BaseSettings):
    SECRET_KEY: SecretStr = Field(
        os.getenv("SECRET_KEY", "c4[0inse4gv4a]")
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DB_NAME: Optional[str] = os.getenv("DB_NAME", "db")

    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", 'abcd')
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", 'abcd')
    REDIRECT_URI: str = os.getenv(
        "REDIRECT_URI", "http://localhost:8000/auth/callback")


# A singleton to avoid reloading it from the env everytime
SETTINGS = _Settings()

#################################### Postgres DATABASE #####################################
# PostgreSQL
DATABASE_URL = f"postgresql+asyncpg://{os.getenv('SQL_USER')}:{os.getenv('SQL_PASSWORD')}@{os.getenv('SQL_HOST', 'db')}/{os.getenv('SQL_DATABASE')}"

# SQLAlchemy engine for syncing operations
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Create a configured "Session" class
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

# declarative base class


class Base(DeclarativeBase):
    pass


######################################### REDIS ############################################
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379")
CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379")

EMAIL_PORT = os.getenv("EMAIL_PORT", 587)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "team@voiceagent.dev")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "abcd1234")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "mapit.automaton@gmail.com")

DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL")
DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD")
DEFAULT_ADMIN_FULLNAME = os.getenv("DEFAULT_ADMIN_FULL_NAME")

# For s3 setup
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=0)

######################################## OPENAI Key ########################################
OPENAI_KEY = os.getenv('OPENAI_KEY')

######################################### LOGGING ##########################################
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)    # Used for logging in other files
