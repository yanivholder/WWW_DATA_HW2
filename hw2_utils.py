from aiohttp import web


def check_basic_validation(request):
    pass


def handle_get_request(request):
    pass


def handle_admin_request(requqst):
    pass


def create_response(text):
    return web.Response(body=text.encode('utf-8'), status=200,
                        headers={"Content-Type": "text/html", "charset": "utf-8"})
