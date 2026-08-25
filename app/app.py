from .schemas import requestOrder, userAuth
from .orders import order, order_book, add_to_buy_orders, add_to_sell_orders, order_id_generator
from .user import User
from .transaction import transaction
from jose import jwt
from fastapi import FastAPI, Depends, HTTPException
from passlib.context import CryptContext
from datetime import datetime 
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import re
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")
ADMIN_USER_PWD = os.getenv("ADMIN_USER_PWD")
ADMIN_USER_EMAIL = os.getenv("ADMIN_USER_EMAIL")
DB_URL = os.getenv("DB_URL")
SQL_DB_CREATION_QUERY_PATH = os.getenv("SQL_DB_CREATION_QUERY")
SQL_TABLE_CREATION_QUERY_PATH = os.getenv("SQL_TABLE_CREATION_QUERY")
SQL_ADMIN_CREATION_QUERY_PATH = os.getenv("SQL_ADMIN_CREATION_QUERY")
STARTING_BALANCE_FOR_A_NEW_USER = os.getenv("STARTING_BALANCE_FOR_A_NEW_USER")
pwd_context = CryptContext(schemes=["bcrypt"])
queries = [SQL_DB_CREATION_QUERY_PATH, SQL_TABLE_CREATION_QUERY_PATH]

engine = create_engine(DB_URL)

# CREATING DATABASE AND TABLES
with engine.connect() as connection:
    for query in queries:
        with open(query, "r") as f:
            db_creation_query = f.read()
        statements = re.split(r";\s*(?=[^']*'[^']*')", db_creation_query)
        for statement in statements:
            statement = statement.strip()
            if statement:
                connection.execute(text(statement))

# ADMIN CREATION
with engine.connect() as connection:
    query = text("""
        INSERT INTO users (email, phone_no, balance) 
        VALUES (:email, NULL, 0)
    """)
    try:
        connection.execute(query, {"email": ADMIN_USER_EMAIL})
        connection.commit()
        print("Admin created successfully.")
    except Exception as e:
        print(f"Error occurred while creating admin user: {e}")
        connection.rollback()

transaction_instance = transaction()
###Creating app
app = FastAPI()

### Helper functions


#Token retriever
oauth2scheme = OAuth2PasswordBearer(tokenUrl="/login")

#login auth checker
async def login_authenticator(token : str = Depends(oauth2scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token corrupted... ")
    user_id = payload.get("user_id")
    with engine.connect() as connection:
        get_user_query = text("""
    SELECT * FROM Users WHERE id = :user_id;
    """)
        try:
            user_object = await connection.execute(get_user_query, {"user_id" : user_id})
            user_object = user_object.scalar_one_or_none()
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database Error")
    if user_object:
        return user_object.id 
    else:
        return None

### Public pages

#Login page
@app.post("/login")
async def login_page(login_details : userAuth):
    user_id = login_details.user_id
    unhashed_pwd = login_details.password
    with engine.connect() as connection:
        pwd_extraction_query = text("""
        SELECT hashed_pwd FROM Users WHERE id = :user_id;
        """)
        try:
            hashed_pwd_object = await connection.execute(pwd_extraction_query, {"user_id" : user_id})
            hashed_pwd = hashed_pwd_object.scalar_one_or_none()
            if not hashed_pwd:
                raise HTTPException(status_code=401, detail= "Wrong Login Credentials.")
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail= "Database Error")
    if pwd_context.verify(unhashed_pwd, hashed_pwd):
        token = jwt.encode({"user_id" : user_id}, SECRET_KEY, algorithm="HS256")
        return {"access_token" : token}
    raise HTTPException(status_code = 401, detail = "Wrong Login Credentials")

#Register page
@app.post("/register")
async def register_page(login_details : userAuth):
    user_id = login_details.user_id
    unhashed_password = login_details.password
    email = login_details.email
    with engine.connect() as connection:
        get_user_query = text("""
            SELECT * FROM Users WHERE id = :user_id;
            """)
        try:
            user_object = await connection.execution(get_user_query, {"user_id", user_id})
            user = user_object.scalar_one_or_none()
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database Error")
    if user:
        raise HTTPException(status_code = 400, detail = "User already exists")
    with engine.connect() as connection:
        verify_if_email_exists_query = text("""
    SELECT * FROM Users WHERE email = :email;
    """)
        try:
            result = await connection.execute(verify_if_email_exists_query, {"email", email})
            email = result.scalar_one_or_none()
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database Error")
    if email:
        raise HTTPException(status_code=400, detail="Email ID already in use.")
    with engine.connect() as connection:
        new_user_appending_query = text("""
        INSERT INTO Users(hashed_pwd, email, balance) VALUES(:hashed_pwd, :email, :STARTING_BALANCE_FOR_A_NEW_USER);
        """)
        try:
            await connection.execute(new_user_appending_query, {"hashed_pwd" : pwd_context.hash(unhashed_password), "email" : email, "STARTING_BALANCE_FOR_A_NEW_USER" : STARTING_BALANCE_FOR_A_NEW_USER})
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database Error")
    token = jwt.encode({"user_id" : user_id}, SECRET_KEY, algorithm="HS256")
    return {"access_token" : token}
    
#Buyer page
@app.post("/buy")
def buyer_page(buy_request : requestOrder,user_id : str = Depends(login_authenticator)):
    buy_order = order(
        order_id=order_id_generator(data["orderbook"], buy_request.symbol),
        user_id=user_id,
        symbol=buy_request.symbol,
        quantity=buy_request.quantity,
        price=buy_request.price,
        status="open",
        filled_quantity=0
    )
    add_to_buy_orders(data["orderbook"], buy_order.order_id, buy_order.user_id, buy_order.symbol, buy_order.quantity, buy_order.price, buy_order.filled_quantity, buy_order.status, buy_order.created_at)
    transaction_instance.trade_stocks(data["orderbook"], buy_request.symbol, data["user_object"])
    return {"Message":"Buy order placed successfully!"}


#seller page
@app.post("/sell")
def seller_page(sell_request : requestOrder, user_id : str = Depends(login_authenticator)):
    sell_order = order(
        order_id=order_id_generator(data["orderbook"], sell_request.symbol),
        user_id=user_id,
        symbol=sell_request.symbol,
        quantity=sell_request.quantity,
        price=sell_request.price,
        status="open",
        filled_quantity=0
    )
    add_to_sell_orders(data["orderbook"], sell_order.order_id, sell_order.user_id, sell_order.symbol, sell_order.quantity, sell_order.price, sell_order.filled_quantity, sell_order.status, sell_order.created_at)
    transaction_instance.trade_stocks(data["orderbook"], sell_request.symbol, data["user_object"])
    return {"Message":"Sell order placed successfully!"}

# market place entire page. look at all the things available in the market
@app.get("/market")
def market_page():
    orderbook = data["orderbook"]
    return {
        "Buy Orders" : {symbol : [orderbook.buy_orders[symbol]] for symbol in orderbook.buy_orders.keys()},
        "Sell Orders" : {symbol : [orderbook.sell_orders[symbol]] for symbol in orderbook.sell_orders.keys()}
    }

# Look at your own portfolio. Different investments and the returns you have gotten. The Florin you have that is liquid and that is in assets. 
@app.get("/portfolio")
def portfolio_page(user_id : str = Depends(login_authenticator)):
    portfolio = data["user_object"].get(user_id)
    if portfolio:
        return portfolio
    else:
        raise HTTPException(status_code=404, detail="User not found. Please login to continue.")

# This is the general news and also company specific news that people can use to place their bets. This should be 2 different APIs but let's do this first
@app.get("/news")
def news_page(user_id : str = Depends(login_authenticator)):
    if data["user_object"].get(user_id):
        pass ### News will be returned only when you are a registered user. 
    else:
        raise HTTPException(status_code=404, detail="User not found. Please login to continue.")

### Only admin pages

# This is where you can look at all the trades that happened from the start of the entire server. 
@app.get("/trade_history")
def history_page(user_id : str = Depends(login_authenticator)):
    if user_id == ADMIN_USER_ID:
        return {"logs": [vars(log) for log in transaction_instance.logger.logs]}
    else:
        raise HTTPException(status_code=403, detail="You donot have access to this data.")

# This is where you can look at the status of your agents that are running the market. 
@app.get("/agents")
def agents_page(user_id : str = Depends(login_authenticator)):
    if user_id == ADMIN_USER_ID:
        pass
    else:
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
