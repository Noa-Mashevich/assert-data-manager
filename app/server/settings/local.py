from .base import *

DEBUG = True

AWS_STACK_STORAGE_CDN = 'e2e-dev-storage-cdn'
AWS_STACK_STORAGE_CDN_REGION = 'us-east-1'
AWS_STACK_STORAGE = 'e2e-dev-storage'
AWS_STACK_UPLOAD = 'e2e-dev-upload'
AWS_STACKS = [
    # the app should not reference its own stack
    # deployment with outputs finishes after the app is already started
    (AWS_STACK_STORAGE_CDN, AWS_STACK_STORAGE_CDN_REGION),
    (AWS_STACK_STORAGE, AWS_REGION),
    (AWS_STACK_UPLOAD, AWS_REGION),
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
