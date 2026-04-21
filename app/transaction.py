import warnings
import heapq

# Every trade log is saved here to later be exported to an SQL database
class trade_logger:
    def __init__(self):
        self.logs = []
    def new_log(self, trade_id, buyer_id, seller_id, symbol, quantity, price):
        self.logs.append(trade_log(trade_id, buyer_id, seller_id, symbol, quantity, price))
    def __len__(self):
        return len(self.logs)
### Base class for each trade log
class trade_log:
    def __init__(self, trade_id, buyer_id, seller_id, symbol, quantity, price):
        self.trade_id = trade_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        
class transaction:
    def __init__(self):
        self.logger = trade_logger()
    def trade_stocks(self, order_book, symbol, users):
        buy_orders = order_book.buy_orders[symbol]
        sell_orders = order_book.sell_orders[symbol]
        trade_ids = []
        while buy_orders and sell_orders:
            trade_id = None
            buy_price, buy_time, buy_order = buy_orders[0]
            sell_price, sell_time, sell_order = sell_orders[0]
            buy_price = -buy_price
            ### using negative of buy_orders price because the heap we have is a hacked version of min_heap -> max_heap conversion. 
            if buy_price >= sell_price:
                if (sell_order.quantity > 0 and buy_order.quantity > 0):
                    if buy_order.user_id != sell_order.user_id:
                        buyer_id = buy_order.user_id
                        seller_id = sell_order.user_id
                        quantity = min(buy_order.quantity, sell_order.quantity)
                        price = sell_order.price
                        if users[buyer_id].cash_balance >= price*quantity:
                            trade_id = self.generate_trade_id()
                            trade_ids.append(trade_id)
                            users[buyer_id].cash_balance -= price * quantity
                            buy_order.filled_quantity += quantity
                            users[seller_id].cash_balance += price * quantity
                            sell_order.filled_quantity += quantity
                            buy_order.quantity -= quantity
                            sell_order.quantity -= quantity
                            if buy_order.quantity == 0:
                                heapq.heappop(buy_orders)
                            if sell_order.quantity == 0:
                                heapq.heappop(sell_orders)
                        else:
                            warnings.warn(f"Buyer {buy_order.user_id} has insufficient funds to execute the trade.")
                            break
                    else:
                        warnings.warn("Buyer and seller cannot be the same user.(You cannot sell to yourself bro.)")
                        break
                else:
                    warnings.warn("One of the orders has zero quantity. Cannot process this trade...")
                    break
            else:
                warnings.warn("No matching orders found.")
                break
            if trade_id:
                self.add_trade_to_logs(trade_id, buyer_id, seller_id, symbol, quantity, price)
        return trade_ids

    # Helper function 1 : adds the trade log to trade log array
    def add_trade_to_logs(self, trade_id, buyer_id, seller_id, symbol, quantity, price):
        self.logger.new_log(trade_id, buyer_id, seller_id, symbol, quantity, price)

    #helper function 2 : creates trade_id that is a 10-digit integer-string. 
    def generate_trade_id(self):
        id = len(self.logger) + 1
        trade_id = str(id).zfill(10)
        return trade_id