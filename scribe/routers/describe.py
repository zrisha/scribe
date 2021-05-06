from fastapi import APIRouter, Request
from ..models import User
from ..lib import find_insert_user

router = APIRouter()

@router.get("/user/{user_id}", tags=["user"], response_model=User)
async def describe_user(request: Request, user_id: str):
  db = request.app.state.db

  user = await find_insert_user(db.users, user_id)
  
  if('error' in user):
    return user['error']
  else:
    return user


