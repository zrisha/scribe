from pydantic import BaseModel, BaseConfig
import datetime
from typing import Optional
from bson import ObjectId

class OID(str):
  @classmethod
  def __get_validators__(cls):
      yield cls.validate

  @classmethod
  def validate(cls, v):
      try:
          return ObjectId(str(v))
      except InvalidId:
          raise ValueError("Not a valid ObjectId")


class MongoModel(BaseModel):
  class Config(BaseConfig):
      allow_population_by_field_name = True
      json_encoders = {
        datetime: lambda dt: dt.isoformat(),
        ObjectId: lambda oid: str(oid),
      }
  id: Optional[OID]

  @classmethod
  def from_mongo(cls, data: dict):
      """We must convert _id into "id". """
      if not data:
          return data
      id = data.pop('_id', None)
      return cls(**dict(data, id=id))

  def to_mongo(self, **kwargs):
      exclude = kwargs.pop('exclude', {'id'})
      exclude_unset = kwargs.pop('exclude_unset', False)
      by_alias = kwargs.pop('by_alias', True)

      parsed = self.dict(
          exclude=exclude,
          exclude_unset=exclude_unset,
          by_alias=by_alias,
          **kwargs,
      )

      # Mongo uses `_id` as default key. We should stick to that as well.
      if '_id' not in parsed and 'id' in parsed:
          parsed['_id'] = parsed.pop('id')

      return parsed