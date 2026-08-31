from sqlalchemy import text
from app.database import engine

def get_stock_id_by_symbol(symbol: str):
    with engine.connect() as connection:
        query = text("SELECT id FROM Stocks WHERE symbol = :symbol")
        return connection.execute(query, {"symbol": symbol}).scalar_one_or_none()

def create_buy_order(user_id: str, stock_id: int, quantity: int, price: float):
    with engine.connect() as connection:
        query = text("""
            INSERT INTO Bids (user_id, stock_id, order_type, quantity, quantity_remaining, price, status)
            VALUES (:user_id, :stock_id, 'buy', :quantity, :quantity, :price, 'open')
        """)
        connection.execute(
            query,
            {
                "user_id": user_id,
                "stock_id": stock_id,
                "quantity": quantity,
                "price": price,
            },
        )
        connection.commit()

def create_sell_order(user_id: str, stock_id: int, quantity: int, price: float):
    with engine.connect() as connection:
        query = text("""
            INSERT INTO Asks (user_id, stock_id, order_type, quantity, quantity_remaining, price, status)
            VALUES (:user_id, :stock_id, 'sell', :quantity, :quantity, :price, 'open')
        """)
        connection.execute(
            query,
            {
                "user_id": user_id,
                "stock_id": stock_id,
                "quantity": quantity,
                "price": price,
            },
        )
        connection.commit()
