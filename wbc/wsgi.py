import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append('/opt/bitnami/projects/wbc')
os.environ.setdefault("PYTHON_EGG_CACHE", "/opt/bitnami/projects/wbc/egg_cache")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wbc.settings")
application = get_wsgi_application()
