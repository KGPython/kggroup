"""
Django settings for kggroup project.

Generated by 'django-admin startproject' using Django 1.8.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ognxg1tv@%3z7%^0#c0#81tcymq4j)$%j_)gk@*luvg3w2#fd^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.122.146','127.0.0.1','localhost']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sellcard',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'sellcard.common.middlewares.KgLoginMiddleware',  #
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'kggroup.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sellcard.views.global_setting',  #
            ],
        },
    },
]

WSGI_APPLICATION = 'kggroup.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
from sellcard.common import Constants
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': Constants.SCM_DB_MYSQL_DATABASE,
        'USER': Constants.SCM_DB_MYSQL_USER,
        'PASSWORD': Constants.SCM_DB_MYSQL_PASSWORD,
        'HOST': Constants.SCM_DB_MYSQL_SERVER,
        'PORT': '3306',
        'ATOMIC_REQUESTS':True,
        # 'AUTOCOMMIT':False,
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT="comm_static"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


KGGROUP_LOGIN_URL ="/kg/sellcard/loginpage/"
KGGROUP_LOGIN_EXEMPT_URLS=["kg/sellcard/login/","kg/sellcard/logout/","kg/sellcard/vcode/","favicon.ico"]
