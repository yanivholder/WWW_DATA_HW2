import os
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
    # TODO: maybe add later aiofiles.os.path....
    return os.path.exists(file_path)
