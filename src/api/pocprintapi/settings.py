import os

from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG') == 'True'

POC_PRINT_HUB_RABBIT_MQ_HOST = os.environ.get('POC_PRINT_HUB_RABBIT_MQ_HOST')
POC_PRINT_HUB_RABBIT_MQ_QUEUE_NAME = os.environ.get('POC_PRINT_HUB_RABBIT_MQ_QUEUE_NAME')
POC_PRINT_HUB_RABBIT_MQ_QUEUE_DURABLE = os.environ.get('POC_PRINT_HUB_RABBIT_MQ_QUEUE_DURABLE') == 'True'
POC_PRINT_HUB_RABBIT_MQ_USERNAME = os.environ.get('POC_PRINT_HUB_RABBIT_MQ_USERNAME')
POC_PRINT_HUB_RABBIT_MQ_PASSWORD = os.environ.get('POC_PRINT_HUB_RABBIT_MQ_PASSWORD')

POC_PRINT_HUB_PRINTER_HOST = os.environ.get('POC_PRINT_HUB_PRINTER_HOST')

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pocprintapi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pocprintapi.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get('DATABASES_POSTGRESQL_NAME'),
        "USER": os.environ.get('DATABASES_POSTGRESQL_USER'),
        "PASSWORD": os.environ.get('DATABASES_POSTGRESQL_PASSWORD'),
        "HOST": os.environ.get('DATABASES_POSTGRESQL_HOST'),
        "PORT": os.environ.get('DATABASES_POSTGRESQL_PORT'),
    }
}

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
