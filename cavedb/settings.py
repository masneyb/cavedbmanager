# Django settings for cavedbmanager project.

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Brian Masney',   'masneyb@onstation.org'),
)

ALLOWED_HOSTS = ( 'localhost', 'private.wvass.org' )

ADMIN_SITE_HEADER = "WVASS Cave Database"

MANAGERS = ADMINS

DATABASES = {
    'default': {
	'ENGINE': 'django.db.backends.postgresql_psycopg2',
	'NAME': 'cavedb',
	'HOST': '/var/run/postgresql/',
    }
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

TIME_ZONE = 'America/New_York'
USE_TZ = False

LANGUAGE_CODE = 'en-us'
SITE_ID = 1

INSTALL_ROOT = os.path.abspath(os.path.dirname(__file__))
if os.sep != '/': INSTALL_ROOT = INSTALL_ROOT.replace(os.sep, '/')

# Specifies where the application is deployed
CONTEXT_PATH = '/'

MEDIA_ROOT = '/usr/local/cavedbmanager-data'
MEDIA_URL = CONTEXT_PATH + 'cavedb/'
STATIC_URL = '/media/'
STATIC_ROOT = 'media/'

SECRET_KEY = 'FIXME_CHANGE_THIS_SECRET_KEY'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'cavedb.middleware.ThreadLocals',
)

ROOT_URLCONF = 'cavedb.urls'

TEMPLATE_DIRS = (
    INSTALL_ROOT + "/templates",
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'cavedb',
)

GIS_CONNECTION_TYPE = 'postgis'
GIS_CONNECTION = 'dbname=wvgis'

