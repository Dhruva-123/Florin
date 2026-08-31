from fastapi import APIRouter, Depends, HTTPException

from app.config import ADMIN_USER_ID
from app.data_access.admin_queries import clear_all_tables, get_trade_history
from app.dependencies import login_authenticator

router = APIRouter()


@router.delete("/clear_database")
def admin_clear_database(user_id: str = Depends(login_authenticator)):
    if str(user_id) != str(ADMIN_USER_ID):
        raise HTTPException(status_code=403, detail="You do not have access to this data.")

    clear_all_tables()
    return {"message": "Database cleared successfully."}


@router.get("/trade_history")
def admin_history_page(user_id: str = Depends(login_authenticator)):
    if str(user_id) != str(ADMIN_USER_ID):
        raise HTTPException(status_code=403, detail="You do not have access to this data.")

    trades = get_trade_history()
    trade_logs = []
    for trade in trades:
        trade_logs.append({
            "id": trade[0],
            "buyer_id": trade[1],
            "seller_id": trade[2],
            "stock_id": trade[3],
            "quantity": trade[4],
            "price": trade[5],
            "created_at": trade[6],
        })
    return {"logs": trade_logs}


@router.get("/agents")
def admin_agents_page(user_id: str = Depends(login_authenticator)):
    if str(user_id) != str(ADMIN_USER_ID):
        raise HTTPException(status_code=403, detail="You do not have access to this data.")
    return {"message": "Agents endpoint placeholder"}
    
