import os
from django.apps import AppConfig


DJANGO_VERIFICATIONS_BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class DjangoVerificationsConfig(AppConfig):
    name = "django_verifications"

    def update_settings(self):

        from django.db import models
        from django.conf import settings

        models.options.DEFAULT_NAMES += ("fields_to_verify", "verification_filters")
        if "widget_tweaks" not in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS.append("widget_tweaks")

        templates = settings.TEMPLATES
        new_templates = []
        for template in templates:
            template["DIRS"].append(
                os.path.join(DJANGO_VERIFICATIONS_BASE_DIR, "templates")
            )
            new_templates.append(template)
        setattr(settings, "TEMPLATES", new_templates)

    def __init__(self, *args, **kwargs):
        super(DjangoVerificationsConfig, self).__init__(*args, **kwargs)
        self.update_settings()

    def ready(self):
        self.update_settings()
