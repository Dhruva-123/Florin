from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from app.database import engine
from app.dependencies import login_authenticator

router = APIRouter()


@router.get("/news")
def news_page(user_id: str = Depends(login_authenticator)):
    with engine.connect() as connection:
        user_query = text("SELECT id FROM Users WHERE id = :user_id")
        user_result = connection.execute(user_query, {"user_id": user_id})
        if not user_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="User not found. Please login to continue.")

        return {"news": [], "message": "News feature coming soon"}
