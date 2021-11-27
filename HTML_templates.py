
def create_html_with_error(error):
    html = f"""
    
    {error}
    
    """
    return html


text = '''
            <!DOCTYPE html>
        <html>
            <head>
                <title> Document Title </title>
            </head>

            <body> 
                <h1> An header </h1>
                <p> The paragraph goes here </p>
                <ul>
                    <li> First item in a list </li>
                    <li> Another item </li>
                </ul>
            </body>
        </html>
    '''