import time
from typing import Optional


# class containing the info that the web request produced
class WebResponse:
    content: Optional[dict]
    status: Optional[int]
    time: int
    success: bool = False
    error: str = None
    error_code: int = None
    error_message: str = None
    from_cache: bool = False

    def __init__(self, content: Optional[dict], status: Optional[int]):
        self.content = content
        self.status = status
        self.time = int(time.time())

    def __bool__(self):
        return self.success


# class containing token info
class BungieToken:
    token: Optional[str]
    error: str = None

    def __init__(self, token: Optional[str]):
        self.token = token
