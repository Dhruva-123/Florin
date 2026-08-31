from fastapi import APIRouter, Depends, HTTPException

from app.data_access.order_queries import create_buy_order, create_sell_order, get_stock_id_by_symbol
from app.dependencies import login_authenticator
from app.schemas import requestOrder

router = APIRouter()


@router.post("/buy")
def buyer_page(buy_request: requestOrder, user_id: str = Depends(login_authenticator)):
    stock_id = get_stock_id_by_symbol(buy_request.symbol)
    if not stock_id:
        raise HTTPException(status_code=404, detail="Stock not found")

    create_buy_order(
        user_id=user_id,
        stock_id=stock_id,
        quantity=int(buy_request.quantity),
        price=buy_request.price,
    )
    return {"Message": "Buy order placed successfully!"}


@router.post("/sell")
def seller_page(sell_request: requestOrder, user_id: str = Depends(login_authenticator)):
    stock_id = get_stock_id_by_symbol(sell_request.symbol)
    if not stock_id:
        raise HTTPException(status_code=404, detail="Stock not found")

    create_sell_order(
        user_id=user_id,
        stock_id=stock_id,
        quantity=int(sell_request.quantity),
        price=sell_request.price,
    )
    return {"Message": "Sell order placed successfully!"}
