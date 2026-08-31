from fastapi import APIRouter

from app.data_access.market_queries import get_market_orders

router = APIRouter()


@router.get("/market")
def market_page():
    return get_market_orders()
