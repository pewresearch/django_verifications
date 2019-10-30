from builtins import object
import re

from django.db import models
from django.apps import apps
from django.contrib.auth.models import User
from django.db.models.signals import class_prepared
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from django_pewtils.abstract_models import BasicExtendedModel

from django_verifications.managers import VerificationManager, VerifiedModelManager
from django_verifications.exceptions import VerifiedFieldLock


class VerifiedModel(BasicExtendedModel):

    """
    An abstract model that is used to designate models in your own application that have one or more fields that
    need to be verified. Models that inherit from this class will have expanded `Meta` options that specify the
    objects and fields to be verified, and have a modified `save` function that protects verified fields from
    being modified.
    """

    objects = VerifiedModelManager().as_manager()

    class Meta(object):

        """
        Additional `Meta` attributes that are required for verification to function properly:
        - `fields_to_verify`: a list of field names corresponding to values that need to be verified
        - `verification_filters`: a list of dictionaries that will be applied as Django filters to select specific
        objects on the model
        """

        abstract = True

        fields_to_verify = []
        verification_filters = []

    def __init__(self, *args, **kwargs):
        """
        Modified `__init__` function to store the original value so that modifications can be tracked and rolled back
        if needed.
        :param args:
        :param kwargs:
        """

        super(VerifiedModel, self).__init__(*args, **kwargs)
        for field in self._meta.fields_to_verify:
            setattr(self, "__init_{}".format(field), getattr(self, field))

    def save(self, *args, **kwargs):

        """
        Modified `save` function that determines whether the object has been verified. If it has been, all verified
        values are checked and if any of them have been changed, a `VerifiedFieldLock` is raised and the save is
        aborted.
        :param args:
        :param kwargs:
        :return:
        """

        try:
            verifiable = self._meta.model.objects.flagged_for_verification().get(
                pk=self.pk
            )
        except self._meta.model.DoesNotExist:
            verifiable = False
        if verifiable:
            for field in self._meta.fields_to_verify:
                good_flags = self.verifications.filter(field=field).filter(is_good=True)
                bad_flags = (
                    self.verifications.filter(field=field)
                    .filter(is_good=False)
                    .filter(corrected=False)
                )
                if good_flags.count() > 0 and bad_flags.count() == 0:
                    original_val = getattr(self, "__init_{}".format(field))
                    current_val = getattr(self, field)
                    if original_val != current_val:
                        setattr(self, field, original_val)
                        raise VerifiedFieldLock(
                            "Cannot modify field {} on object {} due to existing verification (currently '{}', "
                            "attempted to replace with '{}')".format(
                                field, self, original_val, current_val
                            )
                        )

        super(VerifiedModel, self).save(*args, **kwargs)

    def get_verification_metadata(self):

        """
        Returns any information to be provided in the verification interface. The default version of this function
        returns all of the object's values, but this can be overwritten on your own model to return any dictionary
        of values you wish for coders to see in the interface alongside each object.

        :return: A dictionary of values to display in the verification interface
        """

        return list(self.model.objects.filter(pk=self.pk).values())[0]


class Verification(BasicExtendedModel):

    """
    Model that stores verifications. Contains the name of a field, a generic foreign key relation to the object that
    was verified, and the user that verified the field. Also contains any notes the user provided, and a flag
    indicating whether the value has been corrected, if it was originally marked as incorrect.
    """

    field = models.CharField(max_length=150)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="verifications"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    is_good = models.NullBooleanField(null=True)
    notes = models.TextField(null=True)
    corrected = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    objects = VerificationManager().as_manager()


def add_verifications(sender, **kwargs):

    """
    Intercepts any models that inherit from `VerifiedModel` and automatically creates relations with the
    `Verification` model.
    :param sender:
    :param kwargs:
    :return:
    """

    if VerifiedModel in sender.__bases__:
        verifications = GenericRelation(Verification, related_query_name=re.sub(" ", "_", sender._meta.verbose_name))
        verifications.contribute_to_class(sender, "verifications")


class_prepared.connect(add_verifications)
