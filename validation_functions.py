import os
import asyncio
import sqlite3
import aiofiles.os
import aiohttp

import hw2_utils
import config
import db_util
import hw2_utils


def check_basic_validation(request):
    if request.method not in hw2_utils.LEGAL_REQUEST_METHODS:
        return hw2_utils.create_response(body="The request method is not legal. Our "
                                              "server only handles GET, POST and "
                                              "DELETE methods.",
                                         status=400)
    elif not hw2_utils.get_rel_path(request):
        return hw2_utils.create_response(body="The URL is empty",
                                         status=400)
    elif request.version != aiohttp.HttpVersion11:
        return hw2_utils.create_response(body="The HTTP request is not HTTP/1.1",
                                         status=400)


def authenticate_admin(name, pwd):
    if name == config.admin['username'] and pwd == config.admin['password']:
        return True
    else:
        return False


def authenticate_user(name, pwd):
    if authenticate_admin(name, pwd):
        return True
    try:
        return db_util.db_authenticate_user(name, pwd)
    except sqlite3.Error as e:
        return None


async def validate_file_exists(file_path):
    # Better to use aiofiles.os.path.exists but it does not
    # work and we get an OK to use the regular exists in:
    # https://piazza.com/class/kshihhjj74f28h?cid=140
    return os.path.exists(file_path)
