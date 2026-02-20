from werkzeug.wrappers import Request, Response
from werkzeug.test import EnvironBuilder
from app import app as flask_app
import json
import traceback

def handler(request):
    """
    Convert Vercel request to Flask app and return response.
    """
    try:
        # Extract request details - Vercel passes these as dict or Request-like object
        method = getattr(request, 'method', 'GET')
        path = getattr(request, 'path', '/')
        query_string = getattr(request, 'query_string', '') or ''
        headers_dict = getattr(request, 'headers', {}) or {}
        
        # Get body
        body = getattr(request, 'body', None)
        if body is None:
            body = b''
        elif isinstance(body, str):
            body = body.encode('utf-8')
        
        # Build WSGI environ using werkzeug
        builder = EnvironBuilder(
            method=method,
            path=path,
            query_string=query_string,
            data=body,
            headers=headers_dict
        )
        environ = builder.get_environ()
        
        # Create a Flask request context and call the app
        response_data = []
        status_code = None
        response_headers = None
        
        def start_response(status, headers, exc_info=None):
            nonlocal status_code, response_headers
            status_code = int(status.split()[0])
            response_headers = headers
            return lambda s: None
        
        # Call Flask WSGI app
        app_iter = flask_app(environ, start_response)
        
        try:
            for data in app_iter:
                if data:
                    response_data.append(data)
        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()
        
        # Build response
        body_bytes = b''.join(response_data)
        headers_dict = {name: value for name, value in (response_headers or [])}
        
        # Ensure Content-Type is set for HTML
        if 'content-type' not in headers_dict and 'Content-Type' not in headers_dict:
            headers_dict['Content-Type'] = 'text/html; charset=utf-8'
        
        return {
            'statusCode': status_code or 200,
            'headers': headers_dict,
            'body': body_bytes.decode('utf-8', errors='replace'),
        }
    
    except Exception as e:
        # Return detailed error for debugging
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': str(e),
                'type': type(e).__name__,
                'traceback': traceback.format_exc()
            }),
        }
