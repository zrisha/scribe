from fastapi import APIRouter, Request
from ..models import ItemSet, ItemPrescriptions
from ..lib import Elo, find_insert_user

router = APIRouter()

@router.post("/item/elo", tags=["elo"], response_model = ItemPrescriptions)
async def prescribe_item(request: Request, item_set: ItemSet):
  db = request.app.state.db

  user = await find_insert_user(db.users, item_set.user_id)

  if('error' in user):
    return user['error']

  globals = await db.globals.find_one({'app_id': item_set.app_id})

  elo_data = {
    'user': user.dict(),
    'concepts': globals['concepts'],
    'items': globals['items']
  }

  predictions = []
  for item in item_set.dict()['items']:
    e = Elo()
    e.run(1, item_set.user_id, item['id'], item['concepts'], elo_data)
    predictions.append({
      'item': e.predictions['item'][0],
      'concepts': e.predictions['concepts'][0],
      'id': item['id']
    })

  return ItemPrescriptions(
    user_id = item_set.user_id,
    prescriptions = predictions
  )

