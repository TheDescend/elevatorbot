import asyncio
import dataclasses
import time


@dataclasses.dataclass
class RateLimiter:
    """
    Gives out x tokens for network operations every y seconds
    """

    rate: float = 20  # how many requests per second - bungie allows 20/s
    max_tokens: int = 240  # how many requests can we save up - bungie limits after 250 in 10s, so will put that to 240

    tokens: float = dataclasses.field(init=False)
    updated_at: float = dataclasses.field(init=False, default=time.time())

    lock: asyncio.Lock = dataclasses.field(init=False, default=asyncio.Lock())

    def __post_init__(self):
        self.tokens = self.max_tokens
        self.time_for_token = 1 / self.rate

    async def wait_for_token(self):
        """Waits until a token becomes available"""

        async with self.lock:
            if self.tokens == 0:
                now = time.time()
                time_since_update = now - self.updated_at

                # sleep until at least one is ready
                to_sleep = 0
                if time_since_update < self.time_for_token:
                    to_sleep = self.time_for_token - time_since_update
                    await asyncio.sleep(to_sleep)
                    time_since_update += to_sleep

                self.tokens = min(self.tokens + time_since_update * self.rate, self.max_tokens)
                self.updated_at = now + to_sleep

            self.tokens -= 1
