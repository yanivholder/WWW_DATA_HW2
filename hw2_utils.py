import asyncio
import sqlite3
from aiohttp import web
import os
import json
from urllib.parse import parse_qs

import HTML_templates
import db_util

LEGAL_REQUEST_METHODS = ["GET", "POST", "DELETE"]


def check_basic_validation(request):
    if request.method not in LEGAL_REQUEST_METHODS:
        status = 400
        return create_response(body="The request method is not legal. Our "
                                    "server only handles GET, POST and "
                                    "DELETE methods.",
                               status=status)
    # TODO: should we add cases?


def validate_user(user, password):
    pass


def handle_get_request(request):
    if not validate_user(user="", password=""):
        return create_response(body="The user authentication failed.",
                               status=401)
    # TODO: should I use url or rel_url?
    if not os.path.isfile(request.url):
        return create_response(body="The file in the URL not exists.",
                               status=404)
    # TODO: should I add / before the names?
    if request.url in ["/config.py", "/users.db"]:
        return create_response(body="You tried to get forbidden files!",
                               status=403)
    if request.url.endswith(".dp"):
        resp = await handle_dp(request)
    else:
        resp = await handle_readable(request)
    return resp


async def handle_dp(request):
    pass

async def handle_readable(request):
    with open('mime.json', 'r') as mime_file:
        mime_dict = json.load(mime_file)
    _, file_extension = os.path.splitext(request.url)
    if file_extension not in mime_dict:
        # TODO: check what to do in this case
        pass
    with open(request.url, 'rb') as readable_file:
        readable_data = readable_file.read()
    return create_response(body=readable_data,
                           status=200,
                           content_type=mime_dict[file_extension])


def validate_admin():
    return True


def handle_admin_request(request):
    if not validate_admin():
        return create_response(body="Attemp to by non-admin do admin action",
                               status=401)

    try:
        if request.method == "POST":
            parse_dict = parse_qs(request.content)
            username = parse_dict['username']
            pwd = parse_dict['password']
            # username = [parse_dict[i] for i in parse_dict.keys() if 'username' in i][0][0]
            # pwd = [parse_dict[i] for i in parse_dict.keys() if 'password' in i][0][0]
            try:
                db_util.db_create_new_user(username, pwd)
            except sqlite3.DatabaseError as e:
                # tried to add existing username or null value as name or pwd
                return create_response(body="Attemp by admin to register existing username or use null value as name or password",
                                       status=403)

        elif request.method == "DELETE":
            # from DELETE /users/<username> HTTP/1.1\... get the <username>
            username = os.path.basename(request.url)
            db_util.db_delete_user(username)
    except sqlite3.Error as e:
        return create_response(body="DB error", status=500)


def create_http_date():
    """Creates a RFC 1123 format date"""
    from wsgiref.handlers import format_date_time
    from datetime import datetime
    from time import mktime

    now = datetime.now()
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)


def create_response(body, status, content_type="text/html"):
    if status in HTML_templates.ERROR_STATUS_DICT:
        body = HTML_templates.create_html_for_error(text=body, status=status)
        body.encode('utf-8')
    else:
        assert status == 200

    headers = {"charset": "utf-8",
               "Date": create_http_date(),
               "Content-Type": content_type,
               # TODO: check if the content_length is automatically sent
               # "Content-Length":
               # TODO: Add a statement that the server closes the connection upon termination
               }

    return web.Response(body=body, status=status,
                        headers=headers)
