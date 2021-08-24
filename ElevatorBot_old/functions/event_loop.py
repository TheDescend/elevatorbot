import asyncio
import sys


loop = None


def get_asyncio_loop():
    global loop
    if not loop:
        # use different loop for windows. otherwise it breaks
        if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.get_event_loop()
    return loop
