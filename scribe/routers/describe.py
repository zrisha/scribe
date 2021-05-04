from fastapi import APIRouter, Request
from ..models import User

router = APIRouter()


@router.get("/user/{user_id}", tags=["user"], response_model = User)
async def describe_user(request: Request, user_id: str):
  db = request.app.state.db.users

  user = await db.find_one({'user_id': user_id})

  if(user):
    return User.from_mongo(user)
  else:
    user = User(user_id=user_id)
    result = await db.insert_one(user.to_mongo())
    if(result.inserted_id):
      user.id = result.inserted_id
      return user
    else:
      return {"error": "Unknown Database error"}


