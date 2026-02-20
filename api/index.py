import io
import sys
from urllib.parse import unquote

from app import app

def handler(request, response):
    """
    Convert Vercel request/response to WSGI environ/start_response.
    """
    # Build WSGI environ
    environ = {
        'REQUEST_METHOD': request.method,
        'SCRIPT_NAME': '',
        'PATH_INFO': unquote(request.path or '/'),
        'QUERY_STRING': request.query_string or '',
        'CONTENT_TYPE': request.headers.get('content-type', ''),
        'CONTENT_LENGTH': request.headers.get('content-length', ''),
        'SERVER_NAME': request.headers.get('host', 'localhost').split(':')[0],
        'SERVER_PORT': request.headers.get('host', 'localhost').split(':')[1] if ':' in request.headers.get('host', '') else '80',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': io.BytesIO(request.body.encode() if isinstance(request.body, str) else request.body),
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': True,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    
    # Add headers to environ
    for key, value in request.headers.items():
        key = key.upper().replace('-', '_')
        if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ[f'HTTP_{key}'] = value
    
    # Track response status and headers
    status_code = '200 OK'
    response_headers = []
    
    def start_response(status, headers, exc_info=None):
        nonlocal status_code, response_headers
        status_code = status
        response_headers = headers
        return lambda data: None
    
    # Call WSGI app
    app_iter = app(environ, start_response)
    
    # Parse status code and set on response
    code = int(status_code.split()[0])
    response.status(code)
    
    # Add response headers
    for header_name, header_value in response_headers:
        response.setHeader(header_name, header_value)
    
    # Collect response body
    try:
        for data in app_iter:
            if data:
                response.write(data.decode() if isinstance(data, bytes) else data)
    finally:
        if hasattr(app_iter, 'close'):
            app_iter.close()
