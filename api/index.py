import os
import sys
from urllib.parse import parse_qs, urlencode

# Ensure the project root directory is on the Python module search path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app


class VercelRewriteMiddleware:
    """
    WSGI Middleware to guarantee that PATH_INFO matches the user's intended route
    on Vercel, handling Vercel's recent changes to backend framework internal rewrites.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        query_string = environ.get('QUERY_STRING', '')

        # 1. Primary: Extract original path if forwarded via vercel.json query parameter (__path__)
        if '__path__' in query_string:
            params = parse_qs(query_string, keep_blank_values=True)
            if '__path__' in params and params['__path__']:
                orig_path = params.pop('__path__')[0]
                if not orig_path.startswith('/'):
                    orig_path = '/' + orig_path
                environ['PATH_INFO'] = orig_path
                # Clean up query string so Flask views only see their actual parameters
                environ['QUERY_STRING'] = urlencode(params, doseq=True)

        # 2. Fallback: If Vercel routed to the destination script (/api/index or /api/index.py),
        # recover the original URL using Vercel's platform headers.
        elif path_info in ['/api/index.py', '/api/index', '/api'] or path_info.startswith('/api/'):
            matched = (
                environ.get('HTTP_X_MATCHED_PATH') or
                environ.get('HTTP_X_FORWARDED_PATH') or
                environ.get('HTTP_X_FORWARDED_URI') or
                environ.get('HTTP_X_ORIGINAL_URL') or
                '/'
            )
            clean_path = matched.split('?')[0]
            if clean_path in ['/api/index.py', '/api/index', '/api']:
                clean_path = '/'
            environ['PATH_INFO'] = clean_path

        return self.wsgi_app(environ, start_response)


# Apply the middleware to the Flask WSGI application
app.wsgi_app = VercelRewriteMiddleware(app.wsgi_app)
