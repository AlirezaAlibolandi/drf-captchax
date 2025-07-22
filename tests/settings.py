"""
Django settings for running tests.
"""

SECRET_KEY = 'test-key'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'rest_framework',
    'captchax',
    'api',
]

ROOT_URLCONF = 'demo_project.demo_project.urls'

ALLOWED_HOSTS = ['testserver']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

CAPTCHAX = {
    'LENGTH': 6,
    'WIDTH': 200,
    'HEIGHT': 60,
    'FONT_SIZE': 36,
    'BACKGROUND_COLOR': '#ffffff',
    'TEXT_COLOR': '#000000',
    'NOISE_LEVEL': 20,
    'USE_LINES': True,
    'USE_DOTS': True,
    'TIMEOUT': 300,
    'CASE_SENSITIVE': False,
    'MAX_ATTEMPTS': 5,
    'BACKEND': 'captchax.backend.memory.MemoryBackend',
}
