from pydantic import BaseModel, Field
from typing import List



class Prescription(BaseModel):
  id: str
  item: float = Field(gte=0, lte=1)
  concepts: float = Field(gte=0, lte=1)

class ItemPrescriptions(BaseModel):
  user_id: str
  prescriptions: List[Prescription]

class Item(BaseModel):
  id: str
  concepts: List[str]

class ItemSet(BaseModel):
  app_id: str
  user_id: str
  items: List[Item]


