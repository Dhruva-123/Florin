from fastapi import FastAPI

from app.database import ensure_admin_user, initialize_database
from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.market import router as market_router
from app.routes.news import router as news_router
from app.routes.orders import router as orders_router
from app.routes.portfolio import router as portfolio_router

initialize_database()
ensure_admin_user()

app = FastAPI()

app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(market_router)
app.include_router(portfolio_router)
app.include_router(news_router)
app.include_router(admin_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)
