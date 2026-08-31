from sqlalchemy import text

from app.database import engine


def get_user_email_by_id(user_id: str):
    with engine.connect() as connection:
        query = text("SELECT email FROM Users WHERE id = :user_id")
        return connection.execute(query, {"user_id": user_id}).scalar_one_or_none()


def get_trade_history():
    with engine.connect() as connection:
        query = text("""
            SELECT id, buyer_id, seller_id, stock_id, quantity, price_at_trade, created_at
            FROM Transactions
            ORDER BY created_at DESC
        """)
        return connection.execute(query).fetchall()


def clear_all_tables():
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM Transactions"))
        connection.execute(text("DELETE FROM Bids"))
        connection.execute(text("DELETE FROM Asks"))
        connection.execute(text("DELETE FROM Holdings"))
        connection.execute(text("DELETE FROM Users"))
        connection.execute(text("DELETE FROM Stocks"))
        connection.commit()
