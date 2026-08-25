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
        # Check if user_id exists
        get_user_query = text("""
            SELECT * FROM Users WHERE id = :user_id;
            """)
        try:
            user_object = await connection.execute(get_user_query, {"user_id": user_id})
            user = user_object.scalar_one_or_none()
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database Error")
        
        if user:
            raise HTTPException(status_code = 400, detail = "User already exists")
        
        # Check if email exists
        verify_if_email_exists_query = text("""
            SELECT * FROM Users WHERE email = :email;
            """)
        try:
            result = await connection.execute(verify_if_email_exists_query, {"email": email})
            email_exists = result.scalar_one_or_none()
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database Error")
        
        if email_exists:
            raise HTTPException(status_code=400, detail="Email ID already in use.")
        
        # Insert new user
        new_user_appending_query = text("""
        INSERT INTO Users(hashed_pwd, email, balance) VALUES(:hashed_pwd, :email, :balance);
        """)
        try:
            await connection.execute(new_user_appending_query, {"hashed_pwd" : pwd_context.hash(unhashed_password), "email" : email, "balance" : STARTING_BALANCE_FOR_A_NEW_USER})
            connection.commit()
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database Error")
    
    token = jwt.encode({"user_id" : user_id}, SECRET_KEY, algorithm="HS256")
    return {"access_token" : token}
    
#Buyer page
@app.post("/buy")
def buyer_page(buy_request : requestOrder, user_id : str = Depends(login_authenticator)):
    with engine.connect() as connection:
        # Get stock
        stock_query = text("SELECT id FROM stocks WHERE symbol = :symbol")
        stock_result = connection.execute(stock_query, {"symbol": buy_request.symbol})
        stock = stock_result.scalar_one_or_none()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        # Insert buy order
        buy_order_query = text("""
            INSERT INTO bids (user_id, stock_id, order_type, quantity, quantity_remaining, price, status)
            VALUES (:user_id, :stock_id, 'buy', :quantity, :quantity, :price, 'open')
        """)
        try:
            connection.execute(buy_order_query, {
                "user_id": user_id,
                "stock_id": stock,
                "quantity": int(buy_request.quantity),
                "price": buy_request.price
            })
            connection.commit()
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database Error")
    return {"Message":"Buy order placed successfully!"}


#seller page
@app.post("/sell")
def seller_page(sell_request : requestOrder, user_id : str = Depends(login_authenticator)):
    with engine.connect() as connection:
        # Get stock
        stock_query = text("SELECT id FROM stocks WHERE symbol = :symbol")
        stock_result = connection.execute(stock_query, {"symbol": sell_request.symbol})
        stock = stock_result.scalar_one_or_none()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        # Insert sell order
        sell_order_query = text("""
            INSERT INTO asks (user_id, stock_id, order_type, quantity, quantity_remaining, price, status)
            VALUES (:user_id, :stock_id, 'sell', :quantity, :quantity, :price, 'open')
        """)
        try:
            connection.execute(sell_order_query, {
                "user_id": user_id,
                "stock_id": stock,
                "quantity": int(sell_request.quantity),
                "price": sell_request.price
            })
            connection.commit()
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database Error")
    return {"Message":"Sell order placed successfully!"}

# market place entire page. look at all the things available in the market
@app.get("/market")
def market_page():
    with engine.connect() as connection:
        # Get all open bids
        bids_query = text("""
            SELECT b.id, s.symbol, b.price, b.quantity_remaining 
            FROM bids b
            JOIN stocks s ON b.stock_id = s.id
            WHERE b.status = 'open'
            ORDER BY b.price DESC
        """)
        
        # Get all open asks
        asks_query = text("""
            SELECT a.id, s.symbol, a.price, a.quantity_remaining
            FROM asks a
            JOIN stocks s ON a.stock_id = s.id
            WHERE a.status = 'open'
            ORDER BY a.price ASC
        """)
        
        try:
            bids_result = connection.execute(bids_query)
            asks_result = connection.execute(asks_query)
            
            bids_dict = {}
            for bid in bids_result:
                symbol = bid[1]
                if symbol not in bids_dict:
                    bids_dict[symbol] = []
                bids_dict[symbol].append({"id": bid[0], "price": bid[2], "quantity": bid[3]})
            
            asks_dict = {}
            for ask in asks_result:
                symbol = ask[1]
                if symbol not in asks_dict:
                    asks_dict[symbol] = []
                asks_dict[symbol].append({"id": ask[0], "price": ask[2], "quantity": ask[3]})
            
            return {"Buy Orders": bids_dict, "Sell Orders": asks_dict}
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database Error")

# Look at your own portfolio. Different investments and the returns you have gotten. The Florin you have that is liquid and that is in assets. 
@app.get("/portfolio")
def portfolio_page(user_id : str = Depends(login_authenticator)):
    with engine.connect() as connection:
        # Get user balance
        user_query = text("SELECT balance FROM users WHERE id = :user_id")
        user_result = connection.execute(user_query, {"user_id": user_id})
        balance = user_result.scalar_one_or_none()
        if balance is None:
            raise HTTPException(status_code=404, detail="User not found. Please login to continue.")
        
        # Get user holdings
        holdings_query = text("""
            SELECT h.stock_id, s.symbol, h.quantity, h.avg_buy_price
            FROM holdings h
            JOIN stocks s ON h.stock_id = s.id
            WHERE h.user_id = :user_id
        """)
        
        try:
            holdings_result = connection.execute(holdings_query, {"user_id": user_id})
            holdings = []
            for holding in holdings_result:
                holdings.append({
                    "stock_id": holding[0],
                    "symbol": holding[1],
                    "quantity": holding[2],
                    "avg_buy_price": holding[3]
                })
            
            return {"balance": balance, "holdings": holdings}
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database Error")

# This is the general news and also company specific news that people can use to place their bets. This should be 2 different APIs but let's do this first
@app.get("/news")
def news_page(user_id : str = Depends(login_authenticator)):
    with engine.connect() as connection:
        # Verify user exists
        user_query = text("SELECT id FROM users WHERE id = :user_id")
        user_result = connection.execute(user_query, {"user_id": user_id})
        if not user_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="User not found. Please login to continue.")
        
        # TODO: Fetch news from external API
        return {"news": [], "message": "News feature coming soon"}

### Only admin pages

# This is where you can look at all the trades that happened from the start of the entire server. 
@app.get("/trade_history")
def history_page(user_id : str = Depends(login_authenticator)):
    with engine.connect() as connection:
        # Check if admin
        user_query = text("SELECT email FROM users WHERE id = :user_id")
        user_result = connection.execute(user_query, {"user_id": user_id})
        user_email = user_result.scalar_one_or_none()
        
        if user_email != ADMIN_USER_EMAIL:
            raise HTTPException(status_code=403, detail="You do not have access to this data.")
        
        # Get all transactions
        trades_query = text("""
            SELECT id, buyer_id, seller_id, stock_id, quantity, price_at_trade, created_at
            FROM transactions
            ORDER BY created_at DESC
        """)
        
        try:
            trades_result = connection.execute(trades_query)
            trades = []
            for trade in trades_result:
                trades.append({
                    "id": trade[0],
                    "buyer_id": trade[1],
                    "seller_id": trade[2],
                    "stock_id": trade[3],
                    "quantity": trade[4],
                    "price": trade[5],
                    "created_at": trade[6]
                })
            return {"logs": trades}
        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="Database Error")

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