from schemas import requestOrder, userAuth
from orders import order, order_book, add_to_buy_orders, add_to_sell_orders, order_id_generator
from fastapi import FastAPI, Depends, HTTPException
from passlib.context import CryptContext
from user import user
import jwt
from datetime import datetime 
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
pwd_context = CryptContext(schemes=["bcrypt"])

data = {
    "user_object" : {},
    "users_with_password" : {},
    "users_with_email" : {},
    "orderbook": order_book()
}

###Creating app
app = FastAPI()

### Helper functions


#Token retreiver
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
    unhased_password = login_details.password
    if data["users_with_password"].get(user_id) and pwd_context.verify(unhased_password, data["users_with_password"].get(user_id)):
        token = jwt.encode({"user_id" : user_id}, SECRET_KEY, algorithm="HS256")
        return {"access_token" : token}
    raise HTTPException(status_code = 401, detail = "Wrong login credentials...Try again")

#Register page
@app.post("/register")
def register_page(login_details : userAuth):
    user_id = login_details.user_id
    unhased_password = login_details.password
    email = login_details.email
    if data["users_with_password"].get(user_id):
        raise HTTPException(status_code = 400, detail = "User already exists")
    
    if data["users_with_email"].get(user_id):
        raise HTTPException(status_code = 400, detail= "User already exists")
    new_user = user(user_id=user_id, password=pwd_context.hash(unhased_password), email=email)
    data["users_with_password"][user_id] = pwd_context.hash(unhased_password)
    data["users_with_email"][user_id] = email
    new_user.cash_balance = 10000
    new_user.created_at = datetime.now()
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
    data["orderbook"].buy_orders[buy_request.symbol].append(buy_order)
    #add_to_buy_orders()
    return {"Mesage":"Buy order placed successfully!"}


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
    data["orderbook"].sell_orders[sell_request.symbol].append(sell_order)
    #add_to_sell_orders()
    return {"Mesage":"Sell order placed successfully!"}

# market place entire page. look at all the things available in the market
@app.get("/market")
def market_page():
    return data["orderbook"]

# Look at your own portfolio. Different investments and the returns you have gotten. The Florin you have that is liquid and that is in assets. 
@app.get("/portfolio")
def portfolio_page():
    pass

# This is the general news and also company specific news that people can use to place their bets. This should be 2 different APIs but let's do this first
@app.get("/news")
def news_page():
    pass

### Only admin pages

# This is where you can look at all the trades that happened from the start of the entire server. 
@app.get("/trade_history")
def history_page():
    pass

# This is where you can look at the status of your agents that are running the market. 
@app.get("/agents")
def agents_page():
    pass



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)