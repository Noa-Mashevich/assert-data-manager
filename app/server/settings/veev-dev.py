from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('DB_HOSTNAME'),
        'USER': os.getenv('DB_USERNAME'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'NAME': 'studio',
        'PORT': 5432,
        'OPTIONS': {
            'options': '-c search_path=public',
        },
        'CONN_MAX_AGE': 30,
    }
}

AWS_STACK_STORAGE_CDN = 'veev-dev-storage-cdn'
AWS_STACK_STORAGE_CDN_REGION = 'us-east-1'
AWS_STACK_STORAGE = 'veev-dev-storage'
AWS_STACK_UPLOAD = 'veev-dev-upload'
AWS_STACKS = [
    # the app should not reference its own stack
    # deployment with outputs finishes after the app is already started
    (AWS_STACK_STORAGE_CDN, AWS_STACK_STORAGE_CDN_REGION),
    (AWS_STACK_STORAGE, AWS_REGION),
    (AWS_STACK_UPLOAD, AWS_REGION),
]
