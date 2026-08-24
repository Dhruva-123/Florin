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
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")
ADMIN_USER_PWD = os.getenv("ADMIN_USER_PWD")
pwd_context = CryptContext(schemes=["bcrypt"])

data = {
    "user_object" : {},
    "users_with_password" : {},
    "emails" : set(),
    "orderbook": order_book()
}
data["user_object"][ADMIN_USER_ID] = User(user_id=ADMIN_USER_ID, email="Admin@florin.com", password=ADMIN_USER_PWD)
transaction_instance = transaction()
###Creating app
app = FastAPI()

### Helper functions


#Token retriever
oauth2scheme = OAuth2PasswordBearer(tokenUrl="/login")

#login auth checker
def login_authenticator(token : str = Depends(oauth2scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token corrupted... ")
    user_id = payload.get("user_id")
    if data["users_with_password"].get(user_id):
        return user_id
    else:
        raise HTTPException(status_code = 401, detail = "User not found... Go register if you haven't yet!")


### Public pages

#Login page
@app.post("/login")
def login_page(login_details : userAuth):
    user_id = login_details.user_id
    unhashed_password = login_details.password
    if data["users_with_password"].get(user_id) and pwd_context.verify(unhashed_password, data["users_with_password"].get(user_id)):
        token = jwt.encode({"user_id" : user_id}, SECRET_KEY, algorithm="HS256")
        return {"access_token" : token}
    raise HTTPException(status_code = 401, detail = "Wrong login credentials...Try again")

#Register page
@app.post("/register")
def register_page(login_details : userAuth):
    user_id = login_details.user_id
    unhashed_password = login_details.password
    email = login_details.email
    if data["users_with_password"].get(user_id):
        raise HTTPException(status_code = 400, detail = "User already exists")
    if email in data["emails"]:
        raise HTTPException(status_code = 400, detail= "Email already exists")
    new_user = User(user_id=user_id, password=pwd_context.hash(unhashed_password), email=email)
    data["users_with_password"][user_id] = pwd_context.hash(unhashed_password)
    data["emails"].add(email)
    data["user_object"][user_id] = new_user
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
