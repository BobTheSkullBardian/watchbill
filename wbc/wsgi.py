"""
WSGI config for wbc project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import sys
sys.path.append('/opt/bitnami/projects/wbc')
os.environ.setdefault("PYTHON_EGG_CACHE", "/opt/bitnami/projects/wbc/egg_cache")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wbc.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
