import os

with open(os.path.join(os.path.dirname(__file__), "VERSION"), "rb") as version_file:
    __version__ = str(version_file.read()).strip()

default_app_config = "django_verifications.apps.DjangoVerificationsConfig"
