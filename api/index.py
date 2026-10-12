import os
import sys

# Ensure the project root directory is on the Python module search path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app


class VercelPathMiddleware:
    """
    WSGI Middleware to restore the true requested path when running behind
    Vercel serverless rewrites.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')

        # When Vercel rewrites to /api/index.py, restore the real URL path requested by the client
        if path_info in ['/api/index.py', '/api/index', '/api'] or path_info.startswith('/api/index'):
            candidate = (
                environ.get('HTTP_X_FORWARDED_URI') or
                environ.get('HTTP_X_FORWARDED_PATH') or
                environ.get('HTTP_X_ORIGINAL_URL') or
                environ.get('RAW_URI') or
                environ.get('REQUEST_URI') or
                environ.get('HTTP_X_MATCHED_PATH') or
                '/'
            )
            clean = candidate.split('?')[0]
            if clean and clean not in ['/api/index.py', '/api/index', '/api']:
                environ['PATH_INFO'] = clean
            else:
                environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)


app.wsgi_app = VercelPathMiddleware(app.wsgi_app)
