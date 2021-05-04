from typing import Optional
from .mongo import MongoModel, OID
from pydantic import Field

class User(MongoModel):
  user_id: str = Field()
  rating: int = 1000
  count: int = 0
  concepts: dict = {}

