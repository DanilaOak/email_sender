import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import logging

from aiohttp import web
import uvloop

from utils import get_config
from view import routes

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
# 797527984991-1ipji3bp9ueprrrdjmlaukmclrtl4g6f.apps.googleusercontent.com

def create_app(config=None):

    if not config:
        config = get_config()

    cpu_count = multiprocessing.cpu_count()
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app['executor'] = ProcessPoolExecutor(cpu_count)
    app['config'] = config
    app.router.add_routes(routes)
    return app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host=app['config']['HOST'], port=app['config']['PORT'])