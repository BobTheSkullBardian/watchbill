import os
import sys
sys.path.append('/opt/bitnami/projects/wbc')
os.environ.setdefault("PYTHON_EGG_CACHE", "/opt/bitnami/projects/wbc/egg_cache")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wbc.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
