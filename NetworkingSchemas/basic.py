from typing import Optional

from NetworkingSchemas.base import CustomBaseModel


class EmptyResponseModel(CustomBaseModel):
    pass


class NameModel(CustomBaseModel):
    name: Optional[str] = None


class BoolModel(CustomBaseModel):
    bool: bool

    def __bool__(self):
        return self.bool


class ValueModel(CustomBaseModel):
    value: float
