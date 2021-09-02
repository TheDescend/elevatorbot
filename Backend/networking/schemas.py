import dataclasses
import datetime
import time
from typing import Optional

from pydantic import BaseModel


@dataclasses.dataclass
class InternalWebResponse:
    """Internally used class containing the info that the web request produced"""

    content: Optional[dict]
    status: Optional[int]
    time: int = int(time.time())
    success: bool = False
    error: str = None
    error_code: int = None
    error_message: str = None
    from_cache: bool = False

    def __bool__(self):
        return self.success


@dataclasses.dataclass
class WebResponse:
    """This gets returned from an api request"""

    time: int
    status: int
    content: dict
    from_cache: bool

    def __bool__(self):
        return self.status == 200
