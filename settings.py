# Django settings for cavedbmanager project.

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Brian Masney',   'masneyb@onstation.org'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'cavedb'
DATABASE_USER = 'root'
DATABASE_PASSWORD = 'root'
DATABASE_HOST = 'localhost'
DATABASE_PORT = ''

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
AUTH_PROFILE_MODULE = "cavedb.caveuserprofile"

INSTALL_ROOT = os.path.abspath(os.path.dirname(__file__))
if os.sep != '/': INSTALL_ROOT = INSTALL_ROOT.replace(os.sep, '/')

# Specifies where the application is deployed
CONTEXT_PATH = '/'

MEDIA_ROOT = '/usr/local/cavedbmanager-data'
MEDIA_URL = CONTEXT_PATH + 'cavedb/'
ADMIN_MEDIA_PREFIX = '/media/'

SECRET_KEY = 'FIXME_CHANGE_THIS_SECRET_KEY'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'cavedb.middleware.ThreadLocals',
)

ROOT_URLCONF = 'cavedbmanager.urls'

TEMPLATE_DIRS = (
    INSTALL_ROOT + "/templates"
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',

    'cavedbmanager.cavedb',
)

GIS_CONNECTION_TYPE = 'postgis'
GIS_CONNECTION = 'dbname=wvgis'
