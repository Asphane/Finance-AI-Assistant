from pydantic import BaseModel
from datetime import date
from typing import Optional

class TransactionBase(BaseModel):
    date: date
    description: str
    amount: float
    category: str
    type: str

class TransactionCreate(TransactionBase):
    user_id: Optional[str] = None

class Transaction(TransactionBase):
    id: int
    user_id: str

    model_config = {
        "from_attributes": True
    }
