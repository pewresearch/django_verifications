import pandas as pd

from django.conf import settings
from django.apps import apps

from django_pewtils import get_model
from django_pewtils.managers import BasicExtendedManager


class VerifiedModelManager(BasicExtendedManager):

    """
    A manager for use with `VerifiedModel` classes.  Provides functions for filtering objects by verification status.
    """

    def flagged_for_verification(self):

        """
        Selects all objects on the model that have been designated for verification, as specified by the model's
        `verification_filters` Meta attribute.
        :return: A QuerySet of all objects selected for verification
        """

        verifiable = self.all()
        for filter in self.model._meta.verification_filters:
            verifiable = verifiable.filter(**filter)

        return verifiable

    def has_unexamined_fields(self):

        """
        Selects all objects on the model that have one or more fields that need to be verified, as specified by
        the `fields_to_verify` Meta attribute.
        :return: A QuerySet of all objects with at least one unverified field
        """

        return self.flagged_for_verification().exclude(
            pk__in=self.all_fields_examined()
        )

    def all_fields_examined(self):

        """
        Selects all objects on the model that have had all of their fields examined, as specified by the
        `fields_to_verify` Meta attribute.
        :return: A QuerySet of all objects that have had all of their fields examined
        """

        df = pd.DataFrame.from_records(
            self.flagged_for_verification().values(
                "pk", "verifications__field", "verifications__is_good"
            )
        )
        if len(df) > 0 and len(df[~df["verifications__field"].isnull()]) > 0:
            df = df[~df["verifications__field"].isnull()]
            df = df.groupby("pk").agg(lambda x: len(x.unique()))
            df = df[
                df["verifications__field"] == len(self.model._meta.fields_to_verify)
            ]
            return self.filter(pk__in=df.index)
        else:
            return self.none()

    def any_field_incorrect(self):

        """
        Selects all objects on the model that have had one of their fields flagged as being incorrect. Only returns
        objects that have not been corrected.
        :return: A QuerySet of all objects that require correction
        """

        df = pd.DataFrame.from_records(
            self.flagged_for_verification().values(
                "pk",
                "verifications__field",
                "verifications__is_good",
                "verifications__corrected",
            )
        )
        if len(df) > 0 and len(df[~df["verifications__field"].isnull()]) > 0:
            df = df[~df["verifications__field"].isnull()]
            uncorrected_bad_df = (
                df[
                    (df["verifications__is_good"] == False)
                    & (df["verifications__corrected"] == False)
                ]
                .groupby("pk")
                .agg(lambda x: len(x.unique()))
            )
            uncorrected_bad_df = uncorrected_bad_df[
                uncorrected_bad_df["verifications__field"] > 0
            ]
            return self.filter(pk__in=uncorrected_bad_df.index)
        else:
            return self.none()

    def all_fields_good_or_corrected(self):

        """
        Selects all objects on the model that have had all of their fields verified and/or corrected.
        :return: A QuerySet of all objects that have been fully verified (and corrected as needed)
        """

        df = pd.DataFrame.from_records(
            self.flagged_for_verification().values(
                "pk",
                "verifications__field",
                "verifications__is_good",
                "verifications__corrected",
            )
        )
        if len(df) > 0 and len(df[~df["verifications__field"].isnull()]) > 0:
            df = df[~df["verifications__field"].isnull()]
            good_df = (
                df[
                    (df["verifications__is_good"] == True)
                    | (df["verifications__corrected"] == True)
                ]
                .groupby("pk")
                .agg(lambda x: len(x.unique()))
            )
            good_df = good_df[
                good_df["verifications__field"]
                == len(self.model._meta.fields_to_verify)
            ]
            return self.filter(pk__in=good_df.index)
        else:
            return self.none()

    def get_verification_table(self):

        """
        Produces a Pandas DataFrame of all of field values of all of the objects that were flagged for verification
        on the model, along with any verifications or corrections that have been made to those fields.
        :return: Pandas DataFrame
        """

        objects = pd.DataFrame.from_records(self.flagged_for_verification().values())
        verifications = pd.DataFrame.from_records(
            get_model("Verification", app_name="django_verifications")
            .objects.filter_by_model_name(
                self.model._meta.verbose_name.replace(" ", "_")
            )
            .values()
        )
        dfs = []
        for field in verifications["field"].unique():
            vers = verifications.loc[verifications["field"] == field]
            del vers["id"]
            objs = objects[["id", field]]
            objs = objs.merge(vers, how="left", left_on="id", right_on="object_id")
            objs = objs[
                ["id", field, "user_id", "timestamp", "is_good", "notes", "corrected"]
            ]
            dfs.append(objs)
        return pd.concat(dfs)


class VerificationManager(BasicExtendedManager):

    """
    A custom manager for the `Verification` model, allowing you to filter verifications by the model to be corrected,
    along with other utility functions.
    """

    def available_model_names(self):

        """
        Gets the names of the models that have relations to the `Verification` model.
        :return: List of all of the model names, which correspond to the `related_name` on the `Verification` model.
        """

        verification_model_names = []
        for app, model_list in apps.all_models.items():
            for model_name, model in model_list.items():
                if "VerifiedModel" in [base.__name__ for base in model.__bases__]:
                    model_name = model._meta.verbose_name.replace(" ", "_")
                    verification_model_names.append(model_name)
        return verification_model_names

    def filter_by_model_name(self, model_name):

        """
        Filters verifications down to those related to a specific model.
        :param model_name: Name of the related model
        :return: A QuerySet of all verifications related to objects on a specific model
        """

        return self.filter(**{"{}__isnull".format(model_name): False})

    def flagged_for_verification(self, model_name):

        """
        Selects objects from a related model that have been flagged for verification
        :param model_name: Name of the related model
        :return: A QuerySet of objects on the related model that have been flagged for verification
        """

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.flagged_for_verification()

    def has_unexamined_fields(self, model_name):

        """
        Selects objects from a related model that have one or more fields that still need to be examined.
        :param model_name: Name of the related model
        :return: A QuerySet of objects on the related model that haven't been fully examined
        """

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.has_unexamined_fields()

    def all_fields_examined(self, model_name):

        """
        Selects objects from a related model that have had all of their fields examined.
        :param model_name: Name of the related model
        :return: A QuerySet of objects on the related model that have had all of their fields examined
        """

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.all_fields_examined()

    def any_field_incorrect(self, model_name):

        """
        Selects objects from a related model that have had one or more fields examined and marked as incorrect.
        :param model_name: Name of the related model
        :return: A QuerySet of objects with fields that have been marked as incorrect
        """

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.any_field_incorrect()

    def all_fields_good_or_corrected(self, model_name):

        """
        Selects objects from a related model that have had all of their fields examined, verified, and corrected as
        needed.
        :param model_name: Name of the related model
        :return: A QuerySet of objects that have had all of their fields verified and/or corrected
        """

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.all_fields_good_or_corrected()
