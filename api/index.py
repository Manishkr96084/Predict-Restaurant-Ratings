import io
from app import app

def handler(request):
    """
    Convert Vercel request to WSGI environ and call Flask app.
    """
    # Build WSGI environ from Vercel request
    environ = {
        'REQUEST_METHOD': request.method,
        'SCRIPT_NAME': '',
        'PATH_INFO': request.path or '/',
        'QUERY_STRING': request.query_string or '',
        'CONTENT_TYPE': request.headers.get('content-type', ''),
        'CONTENT_LENGTH': request.headers.get('content-length', ''),
        'SERVER_NAME': request.headers.get('host', 'localhost').split(':')[0],
        'SERVER_PORT': '443',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': io.BytesIO(request.body if isinstance(request.body, bytes) else request.body.encode()),
        'wsgi.errors': io.StringIO(),
        'wsgi.multithread': True,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    
    # Add HTTP headers to environ
    for header_name, header_value in request.headers.items():
        header_name = header_name.upper().replace('-', '_')
        if header_name not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{header_name}'] = header_value
    
    # Capture response status and headers
    response_status = None
    response_headers = []
    response_body = []
    
    def start_response(status, headers, exc_info=None):
        nonlocal response_status, response_headers
        response_status = status
        response_headers = headers
        return response_body.append
    
    # Call WSGI app
    app_iter = app(environ, start_response)
    
    try:
        for data in app_iter:
            response_body.append(data)
    finally:
        if hasattr(app_iter, 'close'):
            app_iter.close()
    
    # Extract status code from status string (e.g., "200 OK")
    status_code = int(response_status.split()[0])
    
    # Prepare response headers dict
    headers_dict = {name: value for name, value in response_headers}
    
    # Merge body parts
    body = b''.join(response_body)
    
    # Return Vercel Response
    return {
        'statusCode': status_code,
        'headers': headers_dict,
        'body': body.decode() if isinstance(body, bytes) else body,
    }
