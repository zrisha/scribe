from fastapi import APIRouter, Request
from ..lib import Elo

router = APIRouter()

@router.post("/elo/", tags=["elo"])
async def describe_user(request: Request):
  body = await request.json()

  db = request.app.state.db

  user = db.users.find_one({'user_id': body['user']},{'_id': 0})

  if(user == None):
    user = {
      "user_id": body['user'],
      "rating": 1000,
      "count": 0,
      "concepts": {}
    }
    result = db.users.insert_one(user)
  
  globals = db.globals.find_one({'app_id': body['app_id']},{'_id': 0})


  # elo_data = {
  #   'user': user,
  #   'concepts': {k: v for k, v in globals['concepts'].items() if k in body['concepts']},
  #   'items': {}
  # }
  # elo_data['items'][body['item']] = globals['items'][body['item']]

  elo_data = {
    'user': user,
    'concepts': globals['concepts'],
    'items': globals['items']
  }

  e = Elo()
  e.run(body['result'], body['user'], body['item'], body['concepts'], elo_data)
  db.users.update_one({'user_id': body['user']}, {"$set": e.users[body['user']]})
  db.globals.update_one({'app_id': body['app_id']}, {"$set": {"concepts": e.concepts, "items": e.items}})
  return globals


