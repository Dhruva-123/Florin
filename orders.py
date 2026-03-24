from datetime import datetime

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
        self.created_at = created_at

