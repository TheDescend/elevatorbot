import orjson
from pydantic import BaseModel


class CustomBaseModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson.dumps
