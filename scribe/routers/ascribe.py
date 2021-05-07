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
  
  # Specifies projection, the keys to return from concepts and items
  fields = {f'concepts.{concept}': 1 for concept in event.concepts}
  fields[f'items.{event.item}'] = 1

  globals = await db.globals.find_one({'app_id': event.app_id}, fields)

  elo_data = {
    'user': user.dict(),
    'concepts': globals['concepts'],
    'items': globals['items']
  }

  e = Elo()
  e.match(event.result, event.user_id, event.item, event.concepts, elo_data)

  newUser = User(**e.users[event.user_id])

  update = {f'concepts.{concept}': e.concepts[concept] for concept in e.concepts}
  update[f'items.{event.item}'] = e.items[event.item]

  user_result = await db.users.update_one({'user_id': event.user_id}, {"$set": newUser.dict()})
  global_result = await db.globals.update_one({'app_id': event.app_id}, {"$set": update})

  if(user_result.acknowledged and global_result.acknowledged):
    return newUser
  else:
    return {'error': 'Update failed'}

