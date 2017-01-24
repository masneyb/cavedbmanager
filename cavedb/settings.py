# Copyright 2007-2017 Brian Masney <masneyb@onstation.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

def get_environment_var(name, default_value):
    if name not in os.environ:
        return default_value
    return os.environ[name]


DEBUG = True if get_environment_var('CAVEDB_DEBUG', '1') == '1' else False

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INSTALL_ROOT = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    (get_environment_var('WEB_ADMIN_FULLNAME', 'Your Name'), \
     get_environment_var('WEB_ADMIN_FULLNAME', 'user@domain.org')),
)
MANAGERS = ADMINS

ALLOWED_HOSTS = get_environment_var('CAVEDB_ALLOWED_HOSTS', 'localhost').split(':')

ADMIN_SITE_HEADER = get_environment_var('CAVEDB_SITE_HEADER', 'My Cave Database')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_environment_var('PGDATABASE', 'cavedb'),
        # By default, get the other database connection parameters from the
        # environment variables PGHOST, PGPORT, PGUSER, PGPASSWORD.
    }
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

TIME_ZONE = 'America/New_York'
USE_TZ = False

LANGUAGE_CODE = 'en-us'
SITE_ID = 1

# Specifies where the application is deployed
CONTEXT_PATH = '/'

MEDIA_ROOT = get_environment_var('CAVEDB_DATA_BASE_DIR', '/usr/local/cavedbmanager-data')
GIS_INCLUDES_DIR = MEDIA_ROOT + '/gis_maps'
MEDIA_URL = CONTEXT_PATH + 'cavedb/'
STATIC_URL = '/media/'
STATIC_ROOT = 'media/'

SECRET_KEY = get_environment_var('CAVEDB_SECRET_KEY', 'FIXME_CHANGE_THIS_SECRET_KEY')

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
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

WORKER_FIFO = get_environment_var('CAVEDB_WORKER_FIFO', None)

GIS_CONNECTION_TYPE = 'postgis'
GIS_CONNECTION = 'dbname=wvgis'

# Contents of fonts.list file for Mapserver
# Debian-based systems
GIS_FONTS_LIST = 'opensymbol /usr/share/fonts/truetype/freefont/FreeSansBold.ttf'
# Fedora-based systems
#GIS_FONTS_LIST = 'opensymbol /usr/share/fonts/gnu-free/FreeSansBold.ttf'
