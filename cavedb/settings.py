# Django settings for cavedbmanager project.

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Your Name',   'user@domain.org'),
)

ALLOWED_HOSTS = ( 'localhost' )

ADMIN_SITE_HEADER = "My Cave Database"

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

MEDIA_ROOT = '/usr/local/cavedbmanager-data/'
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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    'django.middleware.security.SecurityMiddleware',
    'cavedb.middleware.ThreadLocals',
)

ROOT_URLCONF = 'cavedb.urls'

# FIXME - this came from a brand new run of `python manage.py startproject`
#TEMPLATES = [
#    {
#        'BACKEND': 'django.template.backends.django.DjangoTemplates',
#        'DIRS': [],
#        'APP_DIRS': True,
#        'OPTIONS': {
#            'context_processors': [
#                'django.template.context_processors.debug',
#                'django.template.context_processors.request',
#                'django.contrib.auth.context_processors.auth',
#                'django.contrib.messages.context_processors.messages',
#            ],
#        },
#    },
#]

TEMPLATE_DIRS = (
    INSTALL_ROOT + "/templates",
)

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

GIS_CONNECTION_TYPE = 'postgis'
GIS_CONNECTION = 'dbname=wvgis'

