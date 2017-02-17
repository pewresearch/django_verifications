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

VERIFICATION_FIELDS = ('enable_verification', 'fields_to_verify', 'verification_metadata_fields', 'verification_filters')
models.options.DEFAULT_NAMES += VERIFICATION_FIELDS

if not getattr(settings, 'VERIFICATION_BASE_MODEL', None):
    VERIFICATION_BASE_MODEL = models.Model
if not getattr(settings, 'VERIFICATION_BASE_MANAGER', None):
    from pewtils.django.managers import BasicManager
    VERIFICATION_BASE_MANAGER = BasicManager
    #VERIFICATION_BASE_MANAGER = models.QuerySet

