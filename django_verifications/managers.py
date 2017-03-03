import pandas

from django.conf import settings
from django.apps import apps

from pewtils.django import get_model

from django_verifications.settings import DJANGO_VERIFICATIONS_FIELDS, DJANGO_VERIFICATIONS_BASE_MODEL, DJANGO_VERIFICATIONS_BASE_MANAGER


class VerifiedModelManager(DJANGO_VERIFICATIONS_BASE_MANAGER):

    def verified(self):

        df = pandas.DataFrame.from_records(self.values("pk", "verifications__field", "verifications__is_good"))
        df = df[~df['verifications__field'].isnull()]
        if len(df) > 0:
            df = df.groupby("pk").agg(lambda x: len(x.unique()))
            df = df[df['verifications__field'] == len(self.model._meta.fields_to_verify)]
            return self.filter(pk__in=df.index)
        else:
            return self.none()

    def verified_good(self):

        df = pandas.DataFrame.from_records(self.values("pk", "verifications__field", "verifications__is_good"))
        df = df[~df['verifications__field'].isnull()]
        if len(df) > 0:
            good_df = df[df['verifications__is_good'] == True].groupby("pk").agg(lambda x: len(x.unique()))
            good_df = good_df[good_df['verifications__field'] == len(self.model._meta.fields_to_verify)]
            return self.filter(pk__in=good_df.index)
        else:
            return self.none()

    def verified_bad(self):

        df = pandas.DataFrame.from_records(self.values("pk", "verifications__field", "verifications__is_good"))
        df = df[~df['verifications__field'].isnull()]
        if len(df) > 0:
            bad_df = df[df['verifications__is_good'] == False].groupby("pk").agg(lambda x: len(x.unique()))
            bad_df = bad_df[bad_df['verifications__field'] > 0]
            return self.filter(pk__in=bad_df.index)
        else:
            return self.none()

    def verifiable(self):

        verifiable = self.all()
        for filter in self.model._meta.verification_filters:
            verifiable = verifiable.filter(**filter)

        return verifiable

    def unverified(self):

        return self.verifiable().exclude(pk__in=self.verified())


class VerificationManager(DJANGO_VERIFICATIONS_BASE_MANAGER):

    def available_model_names(self):

        verification_model_names = []
        for app, model_list in apps.all_models.iteritems():
            for model_name, model in model_list.iteritems():
                if model.__base__.__name__ == "VerifiedModel":
                    verification_model_names.append(model._meta.verbose_name)
        return verification_model_names

    def filter_by_model_name(self, model_name):

        return self.filter(**{"{}__isnull".format(model_name): False})

    def verified_objects(self, model_name):

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.verified()

    def verified(self, model_name):

        return self.filter(**{"{}_id__in".format(model_name): self.verified_objects(model_name).values_list("pk", flat=True)})

    def good_objects(self, model_name):

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.verified_good()

    def good(self, model_name):

        return self.filter(**{"{}_id__in".format(model_name): self.good_objects(model_name).values_list("pk", flat=True)})

    def bad_objects(self, model_name):

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.verified_bad()

    def bad(self, model_name):

        return self.filter(**{"{}_id__in".format(model_name): self.bad_objects(model_name).values_list("pk", flat=True)})

    def verifiable_objects(self, model_name):

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.verifiable()

    def unverified_objects(self, model_name):

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.unverified()

