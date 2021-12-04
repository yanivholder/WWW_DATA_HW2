import os
import base64
import asyncio
import sqlite3

import aiofiles.os

import config
import db_util
import hw2_utils


def check_basic_validation(request):
    if request.method not in hw2_utils.LEGAL_REQUEST_METHODS:
        status = 400
        return hw2_utils.create_response(body="The request method is not legal. Our "
                                              "server only handles GET, POST and "
                                              "DELETE methods.",
                                         status=status)


def parse_username_password_basic(request):
    msg_dict = {pair[0].decode('utf-8'): pair[1] for pair in request.message.raw_headers}
    if 'Authorization' not in msg_dict.keys() or 'Basic' not in msg_dict['Authorization'].decode('utf-8'):
        return None, None

    user_pwd = base64.b64decode(str(msg_dict['Authorization'].decode('utf-8'))[6:]).decode('utf-8').split(':')
    username = user_pwd[0]
    password = user_pwd[1]
    return username, password


def validate_admin(request):
    name, pwd = parse_username_password_basic(request)
    if name == config.admin['username'] and pwd == config.admin['password']:
        print("admin verified")
        return True
    else:
        print("admin access denied")
        return False


def validate_user(request):
    if validate_admin(request):
        return True

    name, pwd = parse_username_password_basic(request)
    try:
        return db_util.db_authenticate_user(name, pwd)
    except sqlite3.Error as e:
        return None





async def validate_file_exists(file_path):
    # TODO: maybe add later aiofiles.os.path....
    return os.path.exists(file_path)
