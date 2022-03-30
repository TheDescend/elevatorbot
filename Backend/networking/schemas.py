import dataclasses
import datetime
import inspect
import time as py_time
from typing import Optional


@dataclasses.dataclass()
class WebResponse:
    """This gets returned from an api request"""

    time: datetime.datetime
    status: int
    content: dict
    from_cache: bool

    def __bool__(self):
        return self.status == 200

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**{k: v for k, v in data.items() if k in inspect.signature(cls).parameters})
