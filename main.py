from fastapi import FastAPI

sell_orders = []
buy_orders = []

app = FastAPI()
@app.post("/buy")
def buyer_page():
    return {{"Hello" : "Buyer!"}
            {"Hello" : "Buyer!"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)