import asyncio
from aiohttp import web

import config
from hw2_utils import *
import validation_functions

SERVER_HOST = 'localhost'
SERVER_PORT = config.port
HOME_PAGE = "http://" + SERVER_HOST + f":{SERVER_PORT}/"


async def handler(request):
    print(request)
    try:
        resp = validation_functions.check_basic_validation(request)
        if resp is not None:
            return resp
        if request.method == "GET":
            print("before handle_get_request")
            resp = await handle_get_request(request)
            print("after handle_get_request")
            return resp
        elif request.method == "POST" or request.method == "DELETE":
            return handle_admin_request(request)
    except:
        return create_response(body="Some server error occurred",
                               status=500)


async def main():
    server = web.Server(handler)
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, SERVER_HOST, SERVER_PORT, shutdown_timeout=config.timeout)
    await site.start()

    print(f"======= Serving on {HOME_PAGE} ======")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(main())
    loop.run_forever()
