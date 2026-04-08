from datetime import datetime
import heapq
from collections import defaultdict
### Base order class
class order:
    def __init__(self, order_id, user_id, symbol, requested_quantity, price, filled_quantity = 0, status = "open", created_at = datetime.now()):
        self.order_id = order_id
        self.user_id = user_id
        self.symbol = symbol
        self.quantity = requested_quantity
        self.price = price
        self.filled_quantity = filled_quantity
        self.status = status
        self.created_at = created_at or datetime.now()

class order_book:
    def __init__(self):
        self.buy_orders = defaultdict(list)
        self.sell_orders = defaultdict(list)
        

def add_to_buy_orders(order_book, order_id, user_id, symbol, requested_quantity, price, filled_quantity = 0, status = "open", created_at = datetime.now()):
    current_order = order(order_id, user_id, symbol, requested_quantity, price, filled_quantity, status, created_at)
    heapq.heappush(order_book.buy_orders[symbol], (-price, created_at, current_order))

def add_to_sell_orders(order_book, order_id, user_id, symbol, requested_quantity, price, filled_quantity = 0, status = "open", created_at = datetime.now()):
    current_order = order(order_id, user_id, symbol, requested_quantity, price, filled_quantity, status, created_at)
    heapq.heappush(order_book.sell_orders[symbol], (price, created_at, current_order))