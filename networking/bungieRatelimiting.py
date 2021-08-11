import asyncio
import time


class BungieRateLimiter:
    """
    Gives out x tokens for network operations every y seconds
    Adapted from https://gist.github.com/pquentin/5d8f5408cdad73e589d85ba509091741
    """
    RATE = 20               # how many requests per second - bungie allows 20/s
    MAX_TOKENS = 240        # how many requests can we save up - bungie limits after 250 in 10s, so will put that to 240

    def __init__(self):
        self.tokens = self.MAX_TOKENS
        self.updated_at = time.monotonic()

    async def wait_for_token(self):
        """ waits until a token becomes available """
        while self.tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(0.1)
        assert self.tokens >= 1
        self.tokens -= 1

    def add_new_tokens(self):
        """ Adds a new token if eligible"""
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = time_since_update * self.RATE
        if self.tokens + new_tokens >= 1:
            self.tokens = min(self.tokens + new_tokens, self.MAX_TOKENS)
            self.updated_at = now
