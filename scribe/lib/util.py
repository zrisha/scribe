from ..models import User


async def find_insert_user(db, user_id):
  user = await db.find_one({'user_id': user_id}, {'_id': 0})

  if(user):
    return User(**user)
  else:
    user = User(user_id=user_id)
    result = await db.insert_one(user.dict())
    if(result.acknowledged):
      return user
    else:
      return {"error": "Unknown Database error"}