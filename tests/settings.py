INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'tests',
)

SECRET_KEY = '@qf@1=jp7fh5)z$7^ej-f8+(kd94l0#eefi+5-@zh=_7odep^9'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': '/home/andrei/training.db',
    }
}

ROOT_URLCONF = 'tests.urls'
