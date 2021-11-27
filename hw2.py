import socket
import os
import asyncio
from aiohttp import web

# Define socket host and port
SERVER_HOST = 'localhost'
SERVER_PORT = 8888
HOME_PAGE = "http://" + SERVER_HOST + f":{SERVER_PORT}/"


async def handler(request):
    text = '''
            <!DOCTYPE html>
        <html>
            <head>
                <title> Document Title </title>
            </head>

            <body> 
                <h1> An header </h1>
                <p> The paragraph goes here </p>
                <ul>
                    <li> First item in a list </li>
                    <li> Another item </li>
                </ul>
            </body>
        </html>
    '''
    return web.Response(body=text.encode('utf-8'), status=200,
                        headers={"Content-Type": "text/html", "charset": "utf-8"})


async def main():
    server = web.Server(handler)
    runner = web.ServerRunner(server)
    await runner.setup()
    site = web.TCPSite(runner, SERVER_HOST, SERVER_PORT)
    await site.start()

    print("======= Serving on http://127.0.0.1:8888/ ======")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(main())
    loop.run_forever()