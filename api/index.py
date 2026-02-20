import io
import json
from app import app

def handler(request):
    """
    Convert Vercel request to WSGI environ and call Flask app.
    """
    try:
        # Extract request details safely
        method = request.method if hasattr(request, 'method') else 'GET'
        path = request.path if hasattr(request, 'path') else '/'
        query_string = request.query_string if hasattr(request, 'query_string') else ''
        headers = request.headers if hasattr(request, 'headers') else {}
        body = request.body if hasattr(request, 'body') else b''
        
        # Ensure body is bytes
        if isinstance(body, str):
            body = body.encode()
        elif body is None:
            body = b''
        
        # Build WSGI environ
        environ = {
            'REQUEST_METHOD': method,
            'SCRIPT_NAME': '',
            'PATH_INFO': path or '/',
            'QUERY_STRING': query_string or '',
            'CONTENT_TYPE': headers.get('content-type', '') if isinstance(headers, dict) else '',
            'CONTENT_LENGTH': str(len(body)),
            'SERVER_NAME': 'lambda.amazonaws.com',
            'SERVER_PORT': '443',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': io.BytesIO(body),
            'wsgi.errors': io.StringIO(),
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': True,
        }
        
        # Add HTTP headers safely
        if isinstance(headers, dict):
            for key, value in headers.items():
                key = key.upper().replace('-', '_')
                if key not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                    environ[f'HTTP_{key}'] = value
        
        # Capture response
        status_code = 200
        response_headers = []
        response_body = []
        
        def start_response(status, headers, exc_info=None):
            nonlocal status_code, response_headers
            status_code = int(status.split()[0])
            response_headers = headers
            return lambda s: None
        
        # Call Flask app
        app_iter = app(environ, start_response)
        
        try:
            for data in app_iter:
                if data:
                    response_body.append(data)
        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()
        
        # Build response
        body_content = b''.join(response_body)
        headers_dict = {name: value for name, value in response_headers}
        
        return {
            'statusCode': status_code,
            'headers': headers_dict,
            'body': body_content.decode('utf-8') if isinstance(body_content, bytes) else body_content,
        }
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e), 'trace': error_trace}),
        }
