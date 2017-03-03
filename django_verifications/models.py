import re

from django.db import models
from django.apps import apps
from django.contrib.auth.models import User
from django.db.models.signals import class_prepared
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from django_verifications.settings import DJANGO_VERIFICATIONS_FIELDS, DJANGO_VERIFICATIONS_BASE_MODEL, DJANGO_VERIFICATIONS_BASE_MANAGER
from django_verifications.managers import VerificationManager, VerifiedModelManager



class VerifiedModel(DJANGO_VERIFICATIONS_BASE_MODEL):

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


class Verification(DJANGO_VERIFICATIONS_BASE_MODEL):

    field = models.CharField(max_length=150)
    user = models.ForeignKey(User, related_name="verifications")
    timestamp = models.DateTimeField(auto_now_add=True)
    is_good = models.NullBooleanField(null=True)
    notes = models.TextField(null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = VerificationManager().as_manager()


def add_verifications(sender, **kwargs):

    if sender.__base__ == VerifiedModel:
        verifications = GenericRelation(Verification, related_query_name=re.sub(" ", "_", sender._meta.verbose_name))
        verifications.contribute_to_class(sender, "verifications")

class_prepared.connect(add_verifications)
