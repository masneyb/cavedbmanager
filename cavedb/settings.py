# SPDX-License-Identifier: Apache-2.0

import os
import django
import cavedb.worker_queue

def get_boolean(name, default_val):
    if name not in os.environ:
        return default_val
    return os.environ[name] == '1'


DEBUG = get_boolean('CAVEDB_DEBUG', True)

# Use EMAIL settings for error reporting if DEBUG is set to False
# By default, print the emails out to the console. They can be
# sent out by changing EMAIL_BACKEND to django.core.mail.backends.smtp.EmailBackend
# and updating the other EMAIL_* settings.
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_USE_TLS = get_boolean('EMAIL_USE_TLS', True)
EMAIL_HOST = os.environ.get('EMAIL_HOST', None)
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', None)
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', None)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INSTALL_ROOT = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    (os.environ.get('WEB_ADMIN_FULLNAME', 'Your Name'), \
     os.environ.get('WEB_ADMIN_EMAIL', 'user@domain.org')),
)
MANAGERS = ADMINS

ALLOWED_HOSTS = os.environ.get('CAVEDB_ALLOWED_HOSTS', 'localhost').split(':')

ADMIN_SITE_HEADER = os.environ.get('CAVEDB_SITE_HEADER', 'My Cave Database')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PGDATABASE', 'cavedb'),
        # By default, get the other database connection parameters from the
        # environment variables PGHOST, PGPORT, PGUSER, PGPASSWORD.
        'OPTIONS': {
            'client_encoding': 'utf-8'
        }
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York'
USE_I18N = True
USE_L10N = True
USE_TZ = True

SITE_ID = 1

# Specifies where the application is deployed
CONTEXT_PATH = '/'

MEDIA_ROOT = os.environ.get('CAVEDB_DATA_BASE_DIR', '/usr/local/cavedbmanager-data')
GIS_INCLUDES_DIR = MEDIA_ROOT + '/gis_maps'
MEDIA_URL = CONTEXT_PATH + 'cavedb/'

STATIC_URL = '/static/'
STATIC_ROOT = 'cavedb/static/'

SECRET_KEY = os.environ.get('CAVEDB_SECRET_KEY', 'FIXME_CHANGE_THIS_SECRET_KEY')

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cavedb.middleware.ThreadLocals',
)

ROOT_URLCONF = 'cavedb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                #'django.template.loaders.eggs.load_template_source',
            ],
        },
        'DIRS': ([INSTALL_ROOT + "/templates"]),
    },
]

DATA_UPLOAD_MAX_NUMBER_FIELDS = int(os.environ.get('DATA_UPLOAD_MAX_NUMBER_FIELDS', '1000'))
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('DATA_UPLOAD_MAX_MEMORY_SIZE', '2621440'))

WSGI_APPLICATION = 'cavedb.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cavedb',
)

QUEUE_STRATEGY = cavedb.worker_queue.msg_dir

CAVEDB_WORKER_MSG_DIR = os.environ.get('CAVEDB_WORKER_MSG_DIR', None)

GIS_CONNECTION_TYPE = 'postgis'
GIS_CONNECTION = 'dbname=%s' % (os.environ.get('CAVEDB_GIS_DBNAME', None))

# Contents of fonts.list file for Mapserver
# Debian-based systems
GIS_FONTS_LIST = 'opensymbol /usr/share/fonts/truetype/freefont/FreeSansBold.ttf'
# Fedora-based systems
#GIS_FONTS_LIST = 'opensymbol /usr/share/fonts/gnu-free/FreeSansBold.ttf'

django.setup()
