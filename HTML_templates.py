
HTML_ENDING = '''
    
    </html>
'''

ERROR_STATUS_DICT = {400: "400 Bad Request",
                     401: "401 Unauthorized",
                     403: "403 Forbidden",
                     404: "404 Not Found",
                     409: "409 Conflict",
                     500: "500 Internal Server Error",
                     501: "501 Not Implemented"}


def create_html_header(title):
    return f'''
    <!DOCTYPE html>
    <html>
        <head>
            <title> {title} </title>
        </head>

'''


def create_html_for_error(text, status):
    html_body = f"""
            <body> 
                <h1> OOPS an error occurred </h1>
                <p> {text} </p>
            </body>
    """
    return create_html_header(title=ERROR_STATUS_DICT[status]) + html_body + HTML_ENDING
