# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.db import models

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

DJANGO_VERIFICATIONS_FIELDS = ('fields_to_verify', 'verification_filters')
models.options.DEFAULT_NAMES += DJANGO_VERIFICATIONS_FIELDS

for setting, default in [
]:
    if not getattr(settings, setting, None):
        globals()[setting] = default
    else:
        globals()[setting] = getattr(settings, setting)

INSTALLED_APPS = [
    "widget_tweaks"
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ]
        }
    }
]