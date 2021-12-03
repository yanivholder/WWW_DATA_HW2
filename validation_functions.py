import os
import asyncio
import aiofiles.os

import hw2_utils


def check_basic_validation(request):
    if request.method not in hw2_utils.LEGAL_REQUEST_METHODS:
        status = 400
        return hw2_utils.create_response(body="The request method is not legal. Our "
                                              "server only handles GET, POST and "
                                              "DELETE methods.",
                                         status=status)


def validate_user(user, password):
    return True


def validate_admin():
    return True


async def validate_file_exists(file_path):
    # TODO: maybe add later aiofiles.os.path....
    return os.path.exists(file_path)
