from aiohttp import web
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest


async def metrics(request: web.Request):
    """
    Prometheus metric endpoint
    """

    resp = web.Response(body=generate_latest(REGISTRY))
    resp.content_type = CONTENT_TYPE_LATEST

    return resp
