
HTML_ENDING = '''
    
    </html>
'''


def create_html_header(title):
    return f'''
    <!DOCTYPE html>
    <html>
        <head>
            <title> {title} </title>
        </head>

'''


def create_html_for_error(text, title):
    html_body = f"""
            <body> 
                <h1> OOPS an error occurred </h1>
                <p> {text} </p>
            </body>
    """
    return create_html_header(title) + html_body + HTML_ENDING
