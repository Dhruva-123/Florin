from fastapi import APIRouter, Depends, HTTPException

from app.data_access.portfolio_queries import get_user_balance, get_user_holdings
from app.dependencies import login_authenticator

router = APIRouter()


@router.get("/portfolio")
def portfolio_page(user_id: str = Depends(login_authenticator)):
    balance = get_user_balance(user_id)
    if balance is None:
        raise HTTPException(status_code=404, detail="User not found. Please login to continue.")

    holdings_result = get_user_holdings(user_id)
    holdings = []
    for holding in holdings_result:
        holdings.append({
            "stock_id": holding[0],
            "symbol": holding[1],
            "quantity": holding[2],
            "avg_buy_price": holding[3],
        })

    return {"balance": balance, "holdings": holdings}
