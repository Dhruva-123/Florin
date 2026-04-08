from schemas import requestOrder, userAuth
from orders import order, order_book, add_to_buy_orders, add_to_sell_orders
from fastapi import FastAPI, Depends, HTTPException
from passlib.context import CryptContext
from user import user
import jwt
from datetime import datetime 
import os

SECRET_KEY = os.getenv("SECRET_KEY")
pwd_context = CryptContext(schemes=["bcrypt"])

data = {
    "user_object" : {},
    "users_with_password" : {},
    "users_with_email" : {},
    "orderbook": order_book()
}

### Helper functions
#login auth checker
def login_authenticator(user_id : str, password : str):
    if data["users_with_password"].get(user_id):
        if pwd_context.verify(password, data["users_with_password"].get(user_id)):
            return user_id
        else:
            raise HTTPException(status_code = 401, detail = "Wrong password.")
    else:
        raise HTTPException(status_code = 401, detail = "User not found... Go register if you haven't yet!")

app = FastAPI()
### Public pages

#Login page
@app.post("/login")
def login_page(login_details : userAuth):
    user_id = login_details.user_id
    unhased_password = login_details.password
    email = login_details.email
    if data["users_with_password"].get(user_id) and pwd_context.verify(unhased_password, data["users_with_password"].get(user_id)):
        if data["users_with_email"].get(user_id) and data["users_with_email"].get(user_id) == email:
            token = jwt.encode({"user_id" : user_id}, SECRET_KEY, algorithms=["HS256"])
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
    data["user_object"].get(user_id) = new_user
    token = jwt.encode({"user_id" : user_id}, SECRET_KEY, algorithms=["HS256"])
    return {"access_token" : token}
    
#Buyer page
@app.post("/buy")
def buyer_page(buy_request : requestOrder,user_id : str = Depends(login_authenticator)):
    buy_request = order()
    add_to_buy_orders()
    return {"Mesage":"Buy order placed successfully!"}


#seller page
@app.post("/sell")
def seller_page():
    pass

# market place entire page. look at all the things available in the market
@app.get("/market")
def market_page():
    pass

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