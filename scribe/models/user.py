from pydantic import Field, BaseModel

class User(BaseModel):
  user_id: str = Field()
  rating: int = 1000
  count: int = 0
  concepts: dict = {}

