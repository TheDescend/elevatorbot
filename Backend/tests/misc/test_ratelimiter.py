import time

import bungio
import pytest
from anyio import create_task_group
from bungio.http import RateLimiter


@pytest.mark.asyncio
async def test_ratelimiter():
    limiter = RateLimiter(seconds=1, max_tokens=10)

    # should need more than 2s for that many requests (has to wait for new tokens twice)
    start = time.perf_counter()
    async with create_task_group() as tg:
        for _ in range(30):
            tg.start_soon(lambda: limiter.wait_for_token())
    end = time.perf_counter()
    assert (end - start) >= 2

    # now it should need more than 3s for that many requests (has to wait for new tokens thrice)
    start = time.perf_counter()
    async with create_task_group() as tg:
        for _ in range(30):
            tg.start_soon(lambda: limiter.wait_for_token())
    end = time.perf_counter()
    assert (end - start) >= 3

    # this should go by instantly
    limiter = RateLimiter(seconds=10000, max_tokens=10000)
    start = time.perf_counter()
    async with create_task_group() as tg:
        for _ in range(10000):
            tg.start_soon(lambda: limiter.wait_for_token())
    end = time.perf_counter()
    assert (end - start) < 10

    # test the default config
    limiter = RateLimiter()
    start = time.perf_counter()
    async with create_task_group() as tg:
        for _ in range(260):
            tg.start_soon(lambda: limiter.wait_for_token())
    end = time.perf_counter()
    assert (end - start) >= 10
    assert (end - start) < 20
