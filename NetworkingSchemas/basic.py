from typing import Optional

from pydantic import BaseModel


class EmptyResponseModel(BaseModel):
    pass


class NameModel(BaseModel):
    name: Optional[str] = None


class BoolModel(BaseModel):
    bool: bool

    def __bool__(self):
        return self.bool


class ValueModel(BaseModel):
    value: float
