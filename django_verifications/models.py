import re

from django.db import models
from django.apps import apps
from django.contrib.auth.models import User
from django.db.models.signals import class_prepared
from django.conf import settings

from django_verifications.settings import VERIFICATION_FIELDS, VERIFICATION_BASE_MODEL, VERIFICATION_BASE_MANAGER
from django_verifications.managers import VerificationModelManager, VerifiedModelManager



class VerifiedModel(VERIFICATION_BASE_MODEL):

    objects = VerifiedModelManager().as_manager()

    class Meta:

        abstract=True

        fields_to_verify = []
        verification_metadata_fields = []
        verification_filters = []

    def __init__(self, *args, **kwargs):

        super(VerifiedModel, self).__init__(*args, **kwargs)
        for field in self._meta.fields_to_verify:
            setattr(self, "__init_{}".format(field), getattr(self, field))

    def save(self, *args, **kwargs):

        try: verifiable = self._meta.model.objects.verifiable().get(pk=self.pk)
        except: verifiable = False
        if verifiable:
            for field in self._meta.fields_to_verify:
                verified = self.verifications.filter(field=field).filter(is_good=True)
                if verified.count() > 0:
                    print "checking {}".format(field)
                    original_val = getattr(self, "__init_{}".format(field))
                    current_val = getattr(self, field)
                    if original_val != current_val:
                        print "Warning, cannot modify field {} on object {} due to existing verification (currently '{}', attempted to replace with '{}')".format(
                            field,
                            self,
                            original_val,
                            current_val
                        )
                        setattr(self, field, original_val)

        super(VerifiedModel, self).save(*args, **kwargs)


class VerificationModel(VERIFICATION_BASE_MODEL):

    field = models.CharField(max_length=150)
    user = models.ForeignKey(User, related_name="verifications")
    timestamp = models.DateTimeField(auto_now_add=True)
    is_good = models.NullBooleanField(null=True)
    notes = models.TextField(null=True)

    objects = VerificationModelManager().as_manager()

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
                if model.__base__ == VerifiedModel:
                    # if all([hasattr(model._meta, v) for v in VERIFICATION_FIELDS]) and getattr(model._meta, "enable_verification"):
                    field = models.ForeignKey("{}.{}".format(app, model.__name__), null=True, related_name="verifications")
                    field.contribute_to_class(sender, re.sub(" ", "_", model._meta.verbose_name))

class_prepared.connect(add_foreign_keys)
