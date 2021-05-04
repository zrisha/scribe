from pymongo import MongoClient, errors
import motor.motor_asyncio


def get_db():
  try:
    return motor.motor_asyncio.AsyncIOMotorClient('mongodb://scribe:scribe@mongo:27017/?authSource=admin')
  except Exception as e:
    print("Could not connect to server: %s" % e)
    return None
  except:
    print('Unknown exception')
    return None