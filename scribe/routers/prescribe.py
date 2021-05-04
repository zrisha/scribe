from fastapi import APIRouter, Request
import json
from ..lib import Elo

router = APIRouter()

@router.post("/item/elo", tags=["elo"])
async def prescribe_item(request: Request):
  body = await request.json()

  #print(json.dumps(body, indent=2))
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

  elo_data = {
    'user': user,
    'concepts': globals['concepts'],
    'items': globals['items']
  }

  predictions = []
  for item in body['items']:
    e = Elo()
    e.run(1, body['user'], item['id'], item['concepts'], elo_data)
    predictions.append({
      'item': e.predictions['item'][0],
      'concepts': e.predictions['concepts'][0],
      'id': item['id']
    })

  return predictions

  # e = Elo()
  # e.run(body['result'], body['user'], body['item'], body['concepts'], elo_data)
  # db.users.update_one({'user_id': body['user']}, {"$set": e.users[body['user']]})
  # db.globals.update_one({'app_id': body['app_id']}, {"$set": {"concepts": e.concepts, "items": e.items}})
  # return globals


