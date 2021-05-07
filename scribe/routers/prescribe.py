from fastapi import APIRouter, Request
from ..models import ItemSet, ItemPrescriptions
from ..lib import Elo, find_insert_user
from itertools import chain

router = APIRouter()

@router.post("/item/elo", tags=["elo"], response_model = ItemPrescriptions)
async def prescribe_item(request: Request, item_set: ItemSet):
  db = request.app.state.db

  user = await find_insert_user(db.users, item_set.user_id)

  if('error' in user):
    return user['error']

  concepts = set(chain.from_iterable(
      [item['concepts'] for item in item_set.dict()['items']]
  ))
  concepts = {f'concepts.{concept}': 1 for concept in concepts}
  items = {f'items.{item["id"]}': 1 for item in item_set.dict()['items']}

  globals = await db.globals.find_one({'app_id': item_set.app_id}, {*items, *concepts})

  elo_data = {
    'user': user.dict(),
    'concepts': globals['concepts'],
    'items': globals['items']
  }

  predictions = []
  for item in item_set.dict()['items']:
    e = Elo()
    e.match(1, item_set.user_id, item['id'], item['concepts'], elo_data)
    predictions.append({
      'item': e.predictions['item'][0],
      'concepts': e.predictions['concepts'][0],
      'id': item['id']
    })

  return ItemPrescriptions(
    user_id = item_set.user_id,
    prescriptions = predictions
  )

