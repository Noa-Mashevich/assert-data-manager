import sys
import json
from django.conf import settings


def is_migration():
    return (
        'makemigrations' in sys.argv
        or 'showmigrations' in sys.argv
        or 'migrate' in sys.argv
        or 'flush' in sys.argv
    )


def is_test():
    return 'test' in sys.argv
