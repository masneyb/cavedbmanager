# SPDX-License-Identifier: Apache-2.0

import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ['DJANGO_SETTINGS_MODULE'] = 'cavedb.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cavedb.settings")
sys.path.append('/usr/local/cavedbmanager/cavedb/')
sys.path.append('/usr/local/cavedbmanager/')

# Needed for basic authentication inside Apache
# https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/apache-auth/
#pylint: disable=unused-import,wrong-import-position
from django.contrib.auth.handlers.modwsgi import check_password

#pylint: disable=invalid-name
application = get_wsgi_application()
