#!/usr/bin/env python
"""
HACK to support the Django + nose without django-nose.
Built based on documentation from:
* https://docs.djangoproject.com/en/1.8/topics/testing/advanced/#using-the-django-test-runner-to-test-reusable-applications
* http://nose.readthedocs.org/en/latest/usage.html#basic-usage
"""
import os
import sys

import nose2
from django.conf import settings


if __name__ == '__main__':
    settings.configure()
    settings.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    settings.DJANGO_LIVESYNC = {'PORT': 9001, 'HOST': '127.0.0.1'}
    result = nose2.discover()
    if not result:
        sys.exit(1)
