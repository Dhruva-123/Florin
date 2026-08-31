from sqlalchemy import text

from app.database import engine


def get_market_orders():
    with engine.connect() as connection:
        bids_query = text("""
            SELECT b.id, s.symbol, b.price, b.quantity_remaining
            FROM Bids b
            JOIN Stocks s ON b.stock_id = s.id
            WHERE b.status = 'open'
            ORDER BY b.price DESC
        """)

        asks_query = text("""
            SELECT a.id, s.symbol, a.price, a.quantity_remaining
            FROM Asks a
            JOIN Stocks s ON a.stock_id = s.id
            WHERE a.status = 'open'
            ORDER BY a.price ASC
        """)

        bids_result = connection.execute(bids_query)
        asks_result = connection.execute(asks_query)

        bids_dict = {}
        for bid in bids_result:
            symbol = bid[1]
            if symbol not in bids_dict:
                bids_dict[symbol] = []
            bids_dict[symbol].append({"id": bid[0], "price": bid[2], "quantity": bid[3]})

        asks_dict = {}
        for ask in asks_result:
            symbol = ask[1]
            if symbol not in asks_dict:
                asks_dict[symbol] = []
            asks_dict[symbol].append({"id": ask[0], "price": ask[2], "quantity": ask[3]})

        return {"Buy Orders": bids_dict, "Sell Orders": asks_dict}
