import heapq
import order from orders

def add_to_buy_orders(buy_orders, order_id, user_id, symbol, requested_quantity, price, filled_quantity = 0, status = "open", created_at = datetime.now()):
    current_order = order(order_id, user_id, symbol, requested_quantity, price, filled_quantity, status, created_at)
    heapq.heappush(buy_orders, (-price, current_order))

def add_to_sell_orders(sell_orders, order_id, user_id, symbol, requested_quantity, price, filled_quantity = 0, status = "open", created_at = datetime.now()):
    current_order = order(order_id, user_id, symbol, requested_quantity, price, filled_quantity, status, created_at)
    heapq.heappush(sell_orders, (price, current_order))

