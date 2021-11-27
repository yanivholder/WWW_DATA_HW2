import asyncio
from aiohttp import web

import config
from hw2_utils import *

SERVER_HOST = 'localhost'
SERVER_PORT = config.port
HOME_PAGE = "http://" + SERVER_HOST + f":{SERVER_PORT}/"


async def handler(request):

    resp = check_basic_validation(request)
    if resp is not None:
        return resp
    if request.method == "GET":
        return handle_get_request(request)
    elif request.method == "POST" or request.method == "DELETE":
        return handle_admin_request(request)


async def main():
    server = web.Server(handler)
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, SERVER_HOST, SERVER_PORT, shutdown_timeout=config.timeout)
    await site.start()

    print(f"======= Serving on {HOME_PAGE} ======")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    main_task = asyncio.create_task(main())
    loop.run_forever()
