import asyncio
import base64
import aiofiles
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
    return str(request.path)[1:]


async def handle_get_request(request):
    rel_path = get_rel_path(request)
    print(rel_path)
    if rel_path == '':
        return create_response(body="Home page",
                               status=200)
    exists = await validation_functions.validate_file_exists(rel_path)
    if not exists:
        return create_response(body="The file in the URL does not exists.",
                               status=404)

    if rel_path in ["config.py", "users.db"]:
        return create_response(body="You tried to get forbidden files!",
                               status=403)

    if rel_path.endswith(".dp"):
        name, pwd = parse_username_password_basic(request)
        if name is None:
            # return create_response(body="The user authentication failed.",
            #                        status=401)
            #  by piazza answer https://piazza.com/class/kshihhjj74f28h?cid=112
            return await handle_dp(request, 'None', False)

        auth_status = validation_functions.authenticate_user(name, pwd)
        if auth_status is None:
            return create_response(body="DB error while authenticating user",
                                   status=500)
        else:
            resp = await handle_dp(request, name, auth_status)

    else:
        resp = await handle_readable(rel_path)
    return resp


async def handle_dp(request, username, auth_status):
    user = {"username": username, "authenticated": auth_status}
    params = request.query
    file_data = await get_file_as_lines(get_rel_path(request))
    file_data = [line.decode('utf-8') for line in file_data]

    data = ' '.join(file_data)
    start = data.find("{%")
    while start >= 0:
        end = data.find("%}")
        to_calc = data[start + 2:end]
        to_replace = data[start:end + 2]
        data = data.replace(to_replace, str(eval(to_calc, {"user": user, "params": params})), 1)
        start = data.find("{%")

    return create_response(body=data,
                           status=200)


def parse_username_password_basic(request):
    msg_dict = {pair[0].decode('utf-8'): pair[1] for pair in request.message.raw_headers}
    if 'Authorization' not in msg_dict.keys() or 'Basic' not in msg_dict['Authorization'].decode('utf-8'):
        return None, None

    user_pwd = base64.b64decode(str(msg_dict['Authorization'].decode('utf-8'))[6:]).decode('utf-8').split(':')
    if user_pwd[0] == '':
        return None, None

    username = user_pwd[0]
    password = user_pwd[1]
    return username, password


async def get_file_as_lines(readable_file_path):
    async with aiofiles.open(readable_file_path, 'rb') as readable_file:
        return await readable_file.readlines()


async def get_readable_data(readable_file_path):
    async with aiofiles.open(readable_file_path, 'rb') as readable_file:
        return await readable_file.read()


async def get_json_data(file_path):
    async with aiofiles.open(file_path, 'r') as mime_file:
        mime_data = await mime_file.read()
    return json.loads(mime_data)


async def handle_readable(rel_path):
    mime_dict = await get_json_data('mime.json')
    _, file_extension = os.path.splitext(rel_path)
    # delete the dot of the extension
    file_extension = file_extension[1:]
    if not os.path.isfile(rel_path):
        return create_response(body="The path is not for a file.",
                               status=400)
    readable_data = await get_readable_data(rel_path)
    for extension_dict in mime_dict["mime-mapping"]:
        if file_extension == extension_dict["extension"]:
            return create_response(body=readable_data,
                                   status=200,
                                   content_type=extension_dict["extension"])
    else:
        return create_response(body=readable_data,
                               status=200,
                               content_type='text/plain')


async def handle_admin_request(request):
    name, pswd = parse_username_password_basic(request)
    if not validation_functions.authenticate_admin(name, pswd):
        return create_response(body="Attempt by non-admin to do admin action",
                               status=401)

    try:
        rel_path = get_rel_path(request)
        if request.method == "POST":
            # TODO: should we check the Content-Type header?
            print("POST")
            if rel_path != 'users':
                return create_response(body="POST request with invalid URL",
                                       status=400)
            parse_dict = parse_qs(await request.text())
            username = parse_dict['username'][0]
            pwd = parse_dict['password'][0]
            if ':' in username:
                return create_response(body="POST request with invalid name",
                                       status=400)
            print(f"Adding username:password=({username}:{pwd}) to DB")
            try:
                db_util.db_create_new_user(username, pwd)
                db_util.db_get_all_users()

            except sqlite3.DatabaseError as e:
                # tried to add existing username or null value as name or pwd
                return create_response(body="Attempt by admin to register existing username or use null value"
                                            " as name or password",
                                       status=403)
            return create_response(body=f"user {username} added successfully",
                                   status=200)

        elif request.method == "DELETE":
            print("DELETE")
            username = os.path.basename(rel_path)
            if not rel_path == 'users/' + username:
                return create_response(body="DELETE URL structure is illegal",
                                       status=400)

            print(f"Removing username=({username}) from DB")

            # TODO: maybe add a more specific try and except here too
            if db_util.db_delete_user(username) == 0:
                return create_response(body="Attempt by admin to Delete non-existing username",
                                       status=404)
            db_util.db_get_all_users()
            return create_response(body=f"user {username} deleted successfully",
                                   status=200)

    except sqlite3.Error as e:
        print(e)
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
    headers = {"Date": create_http_date()}
    if status == 401:
        # TODO: check if this is correct
        # TODO: check with browser
        headers["Connection"] = "keep-alive"
        headers["WWW-Authenticate"] = "Basic realm = \"Access to the staging site\""
    else:
        headers["Connection"] = "close"

    # TODO: how to check it is HTTP/1.1
    return web.Response(
        body=body,
        status=status,
        content_type=content_type,
        charset="utf-8",
        headers=headers)
