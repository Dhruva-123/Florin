from datetime import datetime

### Base user class
class user:
    def __init__(self, user_id, email, password):
        self.user_id = user_id
        self.email = email
        self.password = password
        self.cash_balance = 0.0
        self.created_at = datetime.now()

