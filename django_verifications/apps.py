import os
from django.apps import AppConfig


DJANGO_VERIFICATIONS_BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class DjangoVerificationsConfig(AppConfig):
    name = "django_verifications"

    def update_settings(self):

        from django.db import models

        models.options.DEFAULT_NAMES += ("fields_to_verify", "verification_filters")

    def __init__(self, *args, **kwargs):
        super(DjangoVerificationsConfig, self).__init__(*args, **kwargs)
        self.update_settings()

    def ready(self):
        self.update_settings()
