from pydantic import BaseModel, Field, EmailStr
from typing import Literal
from datetime import datetime


class requestOrder(BaseModel):
    symbol : str = Field(min_length = 3, max_length = 4)
    quantity : float = Field(0, ge = 0)
    price : float = Field(0, ge = 0)
    quantity : float = Field(1, gt = 0)
    created_at : datetime = Field(default_factory = datetime.now)

class userAuth(BaseModel):
    user_id : str = Field(min_length = 3, max_length = 20)
    password : str = Field(min_length = 8, max_length = 60)
    email : EmailStr
    



