import re

from django.db import models
from django.apps import apps
from django.contrib.auth.models import User
from django.db.models.signals import class_prepared
from django.conf import settings

from django_verifications.settings import VERIFICATION_FIELDS, VERIFICATION_BASE_MODEL, VERIFICATION_BASE_MANAGER
from django_verifications.managers import VerificationManager


class VerificationModel(VERIFICATION_BASE_MODEL):

    field = models.CharField(max_length=150)
    user = models.ForeignKey(User, related_name="verifications")
    timestamp = models.DateTimeField(auto_now_add=True)
    is_good = models.NullBooleanField(null=True)
    notes = models.TextField(null=True)

    objects = VerificationManager().as_manager()

    class Meta:

        abstract = True

    # TODO: modify this to work (copied from the Document model)
    # def __str__(self):
    #
    #     parent_field = self.get_parent_field()
    #     parent_str = str(parent_field.related_model.objects.get(pk=getattr(self, parent_field.name).pk))
    #     return "{} verified {} at {}: good={}, outdated={}".format(
    #         self.coder.name,
    #         parent_str,
    #         self.timestamp,
    #         self.good,
    #         self.outdated
    #     )
    #
    # def get_parent_field(self):
    #
    #     parent_field = None
    #     for f in self._meta.get_fields():
    #         if f.is_relation and f.one_to_one and hasattr(self, f.name) and is_not_null(getattr(self, f.name)):
    #             parent_field = f
    #     return parent_field


def add_foreign_keys(sender, **kwargs):

    if sender.__base__ == VerificationModel:
        for app, model_list in apps.all_models.iteritems():
            for model_name, model in model_list.iteritems():
                if all([hasattr(model._meta, v) for v in VERIFICATION_FIELDS]) and getattr(model._meta, "enable_verification"):
                    field = models.ForeignKey("{}.{}".format(app, model.__name__), null=True, related_name="verifications")
                    field.contribute_to_class(sender, re.sub(" ", "_", model._meta.verbose_name))

class_prepared.connect(add_foreign_keys)
