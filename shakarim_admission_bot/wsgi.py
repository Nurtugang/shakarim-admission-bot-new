import os
import sys

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

os.environ["DJANGO_SETTINGS_MODULE"] = "shakarim_admission_bot.settings"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()