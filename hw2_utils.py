import asyncio
import sqlite3
from aiohttp import web
import os
import json
from urllib.parse import parse_qs

import HTML_templates
import db_util
import validation_functions

LEGAL_REQUEST_METHODS = ["GET", "POST", "DELETE"]


async def handle_get_request(request):
    # The request.url comes with HOME_PAGE at start. For example:  http://localhost:8001/hw2.py
    # and request.rel_url comes with / at start.
    rel_url = str(request.rel_url)[1:]
    # TODO: change parameters
    if not validation_functions.validate_user(user="", password=""):
        return create_response(body="The user authentication failed.",
                               status=401)

    res, resp = await validation_functions.validate_file_exists(rel_url)
    if not res:
        return create_response(body="The file in the URL not exists.",
                               status=404)
    if rel_url in ["config.py", "users.db"]:
        return create_response(body="You tried to get forbidden files!",
                               status=403)
    if rel_url.endswith(".dp"):
        # resp = await handle_dp(request)
        return create_response(body="DP!",
                               status=403)
    else:
        # resp = await handle_readable(request)
        return create_response(body="READABLE!",
                               status=403)
    return resp


async def handle_dp(request):
    pass


async def get_readable_data(readable_file_path):
    with open(readable_file_path, 'rb') as readable_file:
        return readable_file.read()


async def get_json_data(file_path):
    with open(file_path, 'r') as mime_file:
        return json.load(mime_file)


async def handle_readable(request):
    mime_dict = await get_json_data('mime.json')
    _, file_extension = os.path.splitext(request.url)
    if file_extension not in mime_dict:
        # TODO: check what to do in this case
        pass
    readable_data = await get_readable_data(request.url)
    return create_response(body=readable_data,
                           status=200,
                           content_type=mime_dict[file_extension])


def handle_admin_request(request):
    # TODO: add async support
    if not validation_functions.validate_admin():
        return create_response(body="Attempt by non-admin to do admin action",
                               status=401)

    try:
        if request.method == "POST":
            parse_dict = parse_qs(request.content)
            username = parse_dict['username']
            pwd = parse_dict['password']
            try:
                db_util.db_create_new_user(username, pwd)
            except sqlite3.DatabaseError as e:
                # tried to add existing username or null value as name or pwd
                return create_response(body="Attempt by admin to register existing username or use null value"
                                            " as name or password",
                                       status=403)

        elif request.method == "DELETE":
            username = os.path.basename(request.url)
            # TODO: maybe add a more specific try and except here too
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
