# coding: utf-8
from django.conf import global_settings
import os
import sys
# Django settings for quickbev project.

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'novobev',
        'USER': 'nathan',
        'PASSWORD': '13ceecos',
        'HOST': '',
        'PORT': '',
    }
}

SOUTH_TESTS_MIGRATE = False
FIXTURE_DIRS = (os.path.join(PROJECT_PATH, 'fixtures/'))
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Pacific/Auckland'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-NZ'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, '../media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, '../static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, '../main/static'),
    os.path.join(PROJECT_PATH, '../writer/static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'ybo=b+qoht*t_h*4drx3#qlbw_s&amp;sgx3$vr32%henml&amp;pi=$gp'

X_FRAME_OPTIONS = 'DENY'

DEFAULT_FROM_EMAIL = 'webmaster@broodoo.com'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'topbevltd@gmail.com'
EMAIL_HOST_PASSWORD = 't1mt00M!g'

LOGIN_URL = '/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #for db transactions. Check middleware order if faulty
    'django.middleware.transaction.TransactionMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
)

SERIALIZATION_MODULES = {
    'json': 'wadofstuff.django.serializers.json'
}

ROOT_URLCONF = 'quickbev.urls'

CSRF_COOKIE_NAME = 'csrftoken'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'quickbev.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
        # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_PATH, '../templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'django_tables2',
    'main',
    'writer',
    'submission',
    'washing',
    'billing',
    'orders',
#     'debug_toolbar',
    'django_nose',
    'raven.contrib.django.raven_compat',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

SESSION_COOKIE_AGE = 39600
# 11 hours (longer than a workday, shorter than time between workdays

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'DEBUG',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['sentry'],
            'propagate': True,
            'level': 'INFO',
        },
        'main': {
            'handlers': ['sentry'],
            'level': 'DEBUG',
        },
        'orders': {
            'handlers': ['sentry'],
            'level': 'DEBUG',
        },
        'submission': {
            'handlers': ['sentry'],
            'level': 'DEBUG',
        },
        'washing': {
            'handlers': ['sentry'],
            'level': 'DEBUG',
        },
        'writer': {
            'handlers': ['sentry'],
            'level': 'DEBUG',
        },
        'billing': {
            'handlers': ['sentry'],
            'level': 'DEBUG',
        },
    }
}

RAVEN_CONFIG = {
    'dsn': 'https://5b9f4a5f7ed54abc9b4a7195c111a1f4:34f354e5ff504931be7bab070c92b600@app.getsentry.com/30502',
}

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse'
#         }
#     },
#     'handlers': {
#         'mail_admins': {
#             'level': 'ERROR',
#             'filters': ['require_debug_false'],
#             'class': 'django.utils.log.AdminEmailHandler'
#         }
#     },
#     'loggers': {
#         'django.request': {
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     }
# }

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
#    'django.core.context_processors.csrf',
    'django.core.context_processors.request',
)

VOLUME_UNIT_TYPE = 1
DENSITY_UNIT_TYPE = 2
TEMPERATURE_UNIT_TYPE = 3

BASE_UNIT = {VOLUME_UNIT_TYPE: 1,
             DENSITY_UNIT_TYPE: 5,
             TEMPERATURE_UNIT_TYPE: 8}

BASE_VOLUME_UNIT = 1
BASE_DENSITY_UNIT = 5
BASE_TEMPERATURE_UNIT = 8


INTERNAL_IPS = ('127.0.0.1',)

# Default formats to be used when parsing dates and times from input boxes,
# in order
# See all available format string here:
# http://docs.python.org/library/datetime.html#strftime-behavior
# * Note that these format strings are different from the ones to display dates
DATETIME_INPUT_FORMATS = (
    '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
    '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    '%Y-%m-%d',              # '2006-10-25'
    '%d/%m/%Y %H:%M:%S',     # '25/10/2006 14:30:59'
    '%d/%m/%Y %H:%M:%S.%f',  # '25/10/2006 14:30:59.000200'
    '%d/%m/%Y %H:%M',        # '25/10/2006 14:30'
    '%d/%m/%Y',              # '25/10/2006'
    '%d/%m/%y %H:%M:%S',     # '25/10/06 14:30:59'
    '%d/%m/%y %H:%M:%S.%f',  # '25/10/06 14:30:59.000200'
    '%d/%m/%y %H:%M',        # '25/10/06 14:30'
    '%d/%m/%y',              # '25/10/06'
)

# Default formats to be used when parsing dates from input boxes, in order
# See all available format string here:
# http://docs.python.org/library/datetime.html#strftime-behavior
# * Note that these format strings are different from the ones to display dates
DATE_INPUT_FORMATS = (
    '%d/%m/%Y', '%Y-%m-%d', '%d/%m/%y',  # '25/10/2006','2006-10-25','25/10/06'
    '%b %d %Y', '%b %d, %Y',            # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',            # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',            # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',            # '25 October 2006', '25 October, 2006'
)

try:
    from settings_local import *
except ImportError:
    pass

