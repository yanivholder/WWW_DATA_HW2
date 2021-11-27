from aiohttp import web

import HTML_templates

LEGAL_REQUEST_METHODS = ["GET", "POST", "DELETE"]


def check_basic_validation(request):
    if request.method not in LEGAL_REQUEST_METHODS:
        status = 400
        return create_response(body=HTML_templates.create_html_for_error(title=f"{status} Illegal Method",
                                                                         text="The request method is not legal. Our "
                                                                              "server only handles GET, POST and "
                                                                              "DELETE methods."),
                               status=status,
                               content_type="text/html"
                               )
    # TODO: should we add cases?


def handle_get_request(request):
    pass


def handle_admin_request(request):
    pass


def create_http_date():
    """Creates a RFC 1123 format date"""
    from wsgiref.handlers import format_date_time
    from datetime import datetime
    from time import mktime

    now = datetime.now()
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)


def create_response(body, status, content_type):
    headers = {"charset": "utf-8",
               "Date": create_http_date(),
               "Content-Type": content_type
               }

    return web.Response(body=body.encode('utf-8'), status=status,
                        headers=headers)
