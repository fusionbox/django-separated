SECRET_KEY = 'not a secret'

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.staticfiles',

    'testproject.testproject',

    # This is here for test discovery, you don't need
    # to add it to INSTALLED_APPS.
    'separated',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite_database',
    }
}

ROOT_URLCONF = 'testproject.testproject.urls'

STATIC_URL = '/static/'
DEBUG = True
