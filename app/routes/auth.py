from fastapi import APIRouter, HTTPException
from jose import jwt
from passlib.context import CryptContext

from app.config import SECRET_KEY, STARTING_BALANCE_FOR_A_NEW_USER
from app.data_access.auth_queries import create_user, get_user_by_email, user_exists_by_email, user_exists_by_id
from app.schemas import userAuth

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"])


@router.post("/login")
async def login_page(login_details: userAuth):
    email = login_details.email
    unhashed_pwd = login_details.password

    user_object = get_user_by_email(email)
    if not user_object:
        raise HTTPException(status_code=401, detail="Wrong Login Credentials.")

    user_id, hashed_pwd = user_object

    if pwd_context.verify(unhashed_pwd, hashed_pwd):
        token = jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm="HS256")
        return {"access_token": token}

    raise HTTPException(status_code=401, detail="Wrong Login Credentials")


@router.post("/register")
async def register_page(login_details: userAuth):
    user_id = login_details.user_id
    unhashed_password = login_details.password
    email = login_details.email

    if user_exists_by_id(user_id):
        raise HTTPException(status_code=400, detail="User already exists")

    if user_exists_by_email(email):
        raise HTTPException(status_code=400, detail="Email ID already in use.")

    registered_user_id = create_user(
        hashed_password=pwd_context.hash(unhashed_password),
        email=email,
        balance=STARTING_BALANCE_FOR_A_NEW_USER,
    )

    token = jwt.encode({"user_id": registered_user_id}, SECRET_KEY, algorithm="HS256")
    return {"access_token": token}
