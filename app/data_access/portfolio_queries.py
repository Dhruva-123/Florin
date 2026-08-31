from sqlalchemy import text

from app.database import engine


def get_user_balance(user_id: str):
    with engine.connect() as connection:
        query = text("SELECT balance FROM Users WHERE id = :user_id")
        return connection.execute(query, {"user_id": user_id}).scalar_one_or_none()


def get_user_holdings(user_id: str):
    with engine.connect() as connection:
        query = text("""
            SELECT h.stock_id, s.symbol, h.quantity, h.avg_buy_price
            FROM Holdings h
            JOIN Stocks s ON h.stock_id = s.id
            WHERE h.user_id = :user_id
        """)
        return connection.execute(query, {"user_id": user_id}).fetchall()
