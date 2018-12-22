import os
import logging


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'sd2+&z(gsmltdd2!9-0r2ezj4m+dah3=t-r6^y!z!usc0@$nv5'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'training',
    'statistics',
    'activities.strength',
    'activities.gps',
    'nested_inline',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'el_pagination',
    'compressor',
)


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]


ROOT_URLCONF = 'spartan.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'spartan.wsgi.application'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

COMPRESS_PRECOMPILERS = (
    ('type/x-scss', 'sass --scss {infile} {outfile}'),
)

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

FILES_DIR = "/files/"

STATIC_ROOT = os.path.join(FILES_DIR, 'static/')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, FILES_DIR, 'media/')
MEDIA_URL = os.path.join("/", FILES_DIR, 'media/')

LOGIN_REDIRECT_URL = '/dashboard'
LOGIN_URL = '/login/'

logging.basicConfig(level=logging.INFO)

try:
    from deployment_settings import *
except:
    logging.info('No deployment_settings module, will expect environemnt configuration')

    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
            'NAME': os.environ.get('DB_NAME', 'spartan'),
            'USER': os.environ.get('DB_USER', 'spartan'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', '')
        }
    }

if 'DEBUG' in os.environ:
    from debug_settings import *
