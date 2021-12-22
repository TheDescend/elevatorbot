import dataclasses
import inspect
import time
from typing import Optional


@dataclasses.dataclass
class InternalWebResponse:
    """Internally used class containing the info that the web request produced"""

    content: Optional[dict] = None
    status: Optional[int] = None
    time: int = int(time.time())
    success: bool = False
    error: str = None
    error_code: int = None
    error_message: str = None
    from_cache: bool = False

    def __bool__(self):
        return self.success


@dataclasses.dataclass()
class WebResponse:
    """This gets returned from an api request"""

    time: int
    status: int
    content: dict
    from_cache: bool
    success: bool

    def __bool__(self):
        return self.status == 200

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**{k: v for k, v in data.items() if k in inspect.signature(cls).parameters})
