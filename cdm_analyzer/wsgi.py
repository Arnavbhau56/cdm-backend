# WSGI entry point for gunicorn on Railway.

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cdm_analyzer.settings')
application = get_wsgi_application()
