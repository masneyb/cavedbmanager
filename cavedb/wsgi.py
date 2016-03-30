import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'cavedb.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cavedb.settings")
sys.path.append('/usr/local/cavedbmanager/cavedb/')
sys.path.append('/usr/local/cavedbmanager/')

from django.contrib.auth.handlers.modwsgi import check_password

application = get_wsgi_application()
