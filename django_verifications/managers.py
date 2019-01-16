import pandas

from django.conf import settings
from django.apps import apps

from django_pewtils import get_model
from django_pewtils.managers import BasicExtendedManager


class VerifiedModelManager(BasicExtendedManager):

    def flagged_for_verification(self):

        verifiable = self.all()
        for filter in self.model._meta.verification_filters:
            verifiable = verifiable.filter(**filter)

        return verifiable

    def has_unexamined_fields(self):

        # not all fields have been examined
        return self.flagged_for_verification().exclude(pk__in=self.all_fields_examined())

    def all_fields_examined(self):

        # all fields have been examined at least once
        df = pandas.DataFrame.from_records(self.flagged_for_verification().values("pk", "verifications__field", "verifications__is_good"))
        if len(df) > 0 and len(df[~df['verifications__field'].isnull()]) > 0:
            df = df[~df['verifications__field'].isnull()]
            df = df.groupby("pk").agg(lambda x: len(x.unique()))
            df = df[df['verifications__field'] == len(self.model._meta.fields_to_verify)]
            return self.filter(pk__in=df.index)
        else:
            return self.none()

    def any_field_incorrect(self):

        # any field has is_bad=True/corrected=False
        df = pandas.DataFrame.from_records(self.flagged_for_verification().values("pk", "verifications__field", "verifications__is_good", "verifications__corrected"))
        if len(df) > 0 and len(df[~df['verifications__field'].isnull()]) > 0:
            df = df[~df['verifications__field'].isnull()]
            uncorrected_bad_df = df[(df['verifications__is_good'] == False) & (df['verifications__corrected'] == False)].groupby("pk").agg(lambda x: len(x.unique()))
            uncorrected_bad_df = uncorrected_bad_df[uncorrected_bad_df['verifications__field'] > 0]
            return self.filter(pk__in=uncorrected_bad_df.index)
        else:
            return self.none()

    def all_fields_good_or_corrected(self):

        # all fields are is_good=True or have been corrected
        df = pandas.DataFrame.from_records(self.flagged_for_verification().values("pk", "verifications__field", "verifications__is_good", "verifications__corrected"))
        if len(df) > 0 and len(df[~df['verifications__field'].isnull()]) > 0:
            df = df[~df['verifications__field'].isnull()]
            good_df = df[(df['verifications__is_good'] == True) | (df['verifications__corrected'] == True)].groupby("pk").agg(lambda x: len(x.unique()))
            good_df = good_df[good_df['verifications__field'] == len(self.model._meta.fields_to_verify)]
            return self.filter(pk__in=good_df.index)
        else:
            return self.none()


class VerificationManager(BasicExtendedManager):

    def available_model_names(self):

        verification_model_names = []
        for app, model_list in apps.all_models.items():
            for model_name, model in model_list.items():
                if model.__base__.__name__ == "VerifiedModel":
                    verification_model_names.append(model._meta.verbose_name)
        return verification_model_names

    def filter_by_model_name(self, model_name):

        return self.filter(**{"{}__isnull".format(model_name): False})

    def flagged_for_verification(self, model_name):

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.flagged_for_verification()

    def has_unexamined_fields(self, model_name):

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.has_unexamined_fields()

    def all_fields_examined(self, model_name):

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.all_fields_examined()

    def any_field_incorrect(self, model_name):

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.any_field_incorrect()

    def all_fields_good_or_corrected(self, model_name):

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.all_fields_good_or_corrected()

    # def verified(self, model_name):
    #
    #     return self.filter(**{"{}_id__in".format(model_name): self.verified_objects(model_name).values_list("pk", flat=True)})

    # def good(self, model_name):
    #
    #     return self.filter(**{"{}_id__in".format(model_name): self.good_objects(model_name).values_list("pk", flat=True)})

    # def bad(self, model_name):
    #
    #     return self.filter(**{"{}_id__in".format(model_name): self.bad_objects(model_name).values_list("pk", flat=True)})


