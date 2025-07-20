from pydantic import SecretStr, EmailStr, conint
from typing import Optional
from app.utils.pydantic_base import BaseSchema

# Login Schema for user login details
class LoginUserSchema(BaseSchema):
    username: str
    password: SecretStr  # Using SecretStr to mask passwords in the output

# Token schema for handling token responses
class TokenSchema(BaseSchema):
    access_token: str
    token_type: str

# Registration schema with example in json_schema_extra
class RegisterUserSchema(BaseSchema):
    username: str
    email: EmailStr  # Ensuring that email is a valid email address
    password: SecretStr  # Password is kept secret using SecretStr
    full_name: str
    is_admin: Optional[bool] = None  # Optional admin flag

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "aurokumar926@gmail.com",
                    "email": "aurokumar926@gmail.com",
                    "password": "password",
                    "full_name": "Auro Kumar Soni",
                    "is_admin": False,  # Optional flag example
                },
            ]
        },
    }
    
class VerifyUserSchema(BaseSchema):
    email: EmailStr
    code: int

# User Schema with from_attributes for Pydantic v2 support
class UserSchema(BaseSchema):
    id: int
    username: str
    email: EmailStr  # Ensuring email is properly validated
    full_name: str
    is_admin: bool
    is_verified: bool

# Schema for anonymous user defaults
class AnonymousUserSchema(BaseSchema):
    username: str = "anonymous"
    is_admin: bool = False
