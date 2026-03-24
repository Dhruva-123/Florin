import users from users
import warnings

# Every trade log is saved here to later be exported to an SQL database
trade_logs = []

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
    def trade_stocks(self, buy_orders, sell_orders, symbol):
        trade_id = None
        while buy_orders and sell_orders:
            ### using negative of buy_orders price because the heap we have is a hacked version of min_heap -> max_heap conversion. 
            if -buy_orders[0].price >= sell_orders[0].price and buy_orders[0].symbol == sell_orders[0].symbol:
                if (sell_orders[0].quantity > 0 and buy_orders[0].quantity > 0):
                    if buy_orders[0].user_id != sell_orders[0].user_id:
                        if users[buy_orders[0].user_id].cash_balance >= buy_orders[0].price * min(buy_orders[0].quantity, sell_orders[0].quantity):
                            trade_id = self.genetrate_trade_id()
                            buyer_id = buy_orders[0].user_id
                            seller_id = sell_orders[0].user_id
                            quantity = min(buy_orders[0].quantity, sell_orders[0].quantity)
                            price = sell_orders[0].price
                            users[buyer_id].cash_balance -= price * quantity
                            users[seller_id].cash_balance += price * quantity
                            buy_orders[0].quantity -= quantity
                            sell_orders[0].quantity -= quantity
                            if buy_orders[0].quantity == 0:
                                buy_orders.heappop(0)
                            if sell_orders[0].quantity == 0:
                                sell_orders.heappop(0)
                        else:
                            warnings.warn(f"Buyer {buyer_id} has insufficient funds to execute the trade.")
                            break
                    else:
                        warnings.warn("Buyer and seller cannot be the same user.(You cannot sell to yourself bro.)")
                        break
                else:
                    warnings.warn("One of the orders has zero quantity. Cannot process this trade...")
                    break
            else:
                warnings.warn("No matching orders found.")

        self.add_trade_to_logs(trade_id, buyer_id, seller_id, symbol, quantity, price)
        return trade_id

    # Helper function 1 : adds the trade log to trade log array
    def add_trade_to_logs(self, trade_id, buyer_id, seller_id, symbol, quantity, price):
        trade = trade_log(trade_id, buyer_id, seller_id, symbol, quantity, price)
        trade_log.append(trade)

    #helper function 2 : creates trade_id that is a 10-digit integer-string. 
    def genetrate_trade_id(self):
        id = len(trade_log) + 1
        trade_id = str(id).zfill(10)
        return trade_id