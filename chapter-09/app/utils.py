from app.config import SECRET_TOKEN
import jwt
import bcrypt
import time
from fastapi import HTTPException


def verify_jwt_token(token: str):
    try:
        return jwt.decode(token, SECRET_TOKEN, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_jwt_token(email: str) -> str:
    payload = {
        "sub": email,
        "iss": "stack_example",
        "iat": int(time.time()),
        "exp": int(time.time()) + 7 * 24 * 60 * 60,
    }
    return jwt.encode(payload, SECRET_TOKEN, algorithm="HS256")


def create_password_hash(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def is_password_correct(password: str, passwordhash: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), passwordhash)
