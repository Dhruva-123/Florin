from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import SECRET_KEY
from app.database import engine

oauth2scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def login_authenticator(token: str = Depends(oauth2scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="Token corrupted...")

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token corrupted...")

    with engine.connect() as connection:
        get_user_query = text("""
            SELECT id FROM Users WHERE id = :user_id;
        """)
        try:
            user_object = connection.execute(get_user_query, {"user_id": user_id}).scalar_one_or_none()
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database Error")

    if user_object is not None:
        return user_id
    raise HTTPException(status_code=401, detail="Token corrupted...")
