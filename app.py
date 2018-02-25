import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import logging

from aiohttp import web
import uvloop
from motor import motor_asyncio

from utils import get_config
from view import routes

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

def create_app(config=None):

    if not config:
        config = get_config()

    cpu_count = multiprocessing.cpu_count()
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app['executor'] = ProcessPoolExecutor(cpu_count)
    app['config'] = config
    app.router.add_routes(routes)
    # db connection
    app.client = motor_asyncio.AsyncIOMotorClient(config['MONGO_HOST'])
    app.db = app.client[config['MONGO_DB_NAME']]
    return app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host=app['config']['HOST'], port=app['config']['PORT'])