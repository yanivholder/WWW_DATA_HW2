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


def get_rel_path(request):
    # The request.url comes with HOME_PAGE at start. For example:  http://localhost:8001/hw2.py
    # and request.rel_url comes with / at start.
    return str(request.rel_url)[1:]


async def handle_get_request(request):
    rel_path = get_rel_path(request)
    # TODO: change parameters
    if not validation_functions.validate_user(user="", password=""):
        return create_response(body="The user authentication failed.",
                               status=401)

    exists = await validation_functions.validate_file_exists(rel_path)
    if not exists:
        return create_response(body="The file in the URL does not exists.",
                               status=404)

    if rel_path in ["config.py", "users.db"]:
        return create_response(body="You tried to get forbidden files!",
                               status=403)

    if rel_path.endswith(".dp"):
        # resp = await handle_dp(request)
        return create_response(body="DP!",
                               status=403)
    else:
        resp = await handle_readable(rel_path)
    return resp


async def handle_dp(request):
    pass


async def get_readable_data(readable_file_path):
    with open(readable_file_path, 'rb') as readable_file:
        return readable_file.read()


async def get_json_data(file_path):
    with open(file_path, 'r') as mime_file:
        return json.load(mime_file)


async def handle_readable(rel_path):
    mime_dict = await get_json_data('mime.json')
    _, file_extension = os.path.splitext(rel_path)
    # delete the dot of the extension
    file_extension = file_extension[1:]
    for extension_dict in mime_dict["mime-mapping"]:
        if file_extension == extension_dict["extension"]:
            readable_data = await get_readable_data(rel_path)
            return create_response(body=readable_data,
                                   status=200,
                                   content_type=extension_dict["extension"])
    else:
        # TODO: check what to do in this case
        print(f"{file_extension} not in mime.json")


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
