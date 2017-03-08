# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.db import models

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
# Copied from django_extensions as a boilerplate example
# REPLACEMENTS = {
# }
# add_replacements = getattr(settings, 'EXTENSIONS_REPLACEMENTS', {})
# REPLACEMENTS.update(add_replacements)

from django.db import models

DJANGO_VERIFICATIONS_FIELDS = ('fields_to_verify', 'verification_metadata_fields', 'verification_filters')
models.options.DEFAULT_NAMES += DJANGO_VERIFICATIONS_FIELDS

if not getattr(settings, 'DJANGO_VERIFICATIONS_BASE_MODEL', None):
    # DJANGO_VERIFICATIONS_BASE_MODEL = models.Model
    from pewtils.django.abstract_models import BasicExtendedModel
    DJANGO_VERIFICATIONS_BASE_MODEL = BasicExtendedModel
if not getattr(settings, 'DJANGO_VERIFICATIONS_MANAGER', None):
    from pewtils.django.managers import BasicManager
    DJANGO_VERIFICATIONS_BASE_MANAGER = BasicManager
    #DJANGO_VERIFICATIONS_BASE_MANAGER = models.QuerySet

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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