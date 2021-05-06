from pydantic import BaseModel, Field

class Event(BaseModel):
  app_id: str
  user_id: str
  item: str
  concepts: list
  result: int = Field(gte=0, lte=1)

