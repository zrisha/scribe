from fastapi import APIRouter, Request
from ..lib import Elo
from ..models import User, Event
from ..lib import find_insert_user

router = APIRouter()

@router.post("/elo/", tags=["elo"], response_model = User)
async def ascribe_user(request: Request, event:Event):
  db = request.app.state.db

  user = await find_insert_user(db.users, event.user_id)

  if('error' in user):
    return user['error']
  
  globals = await db.globals.find_one({'app_id': event.app_id})

  elo_data = {
    'user': user.dict(),
    'concepts': globals['concepts'],
    'items': globals['items']
  }

  e = Elo()
  e.match(event.result, event.user_id, event.item, event.concepts, elo_data)

  newUser = User(**e.users[event.user_id])

  user_result = await db.users.update_one({'user_id': event.user_id}, {"$set": newUser.dict()})
  global_result = await db.globals.update_one({'app_id': event.app_id}, {"$set": {"concepts": e.concepts, "items": e.items}})

  if(user_result.acknowledged and global_result.acknowledged):
    return newUser
  else:
    return {'error': 'Update failed'}


