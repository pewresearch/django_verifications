import pandas

from django.conf import settings

from pewtils.django import get_model

from django_verifications.settings import VERIFICATION_FIELDS, VERIFICATION_BASE_MODEL, VERIFICATION_BASE_MANAGER


class VerifiedModelManager(VERIFICATION_BASE_MANAGER):

    def verifiable(self):

        verifiable = self.all()
        for filter in self.model._meta.verification_filters:
            verifiable = verifiable.filter(**filter)

        return verifiable

    def verified_all(self):

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

        return self.verifiable().exclude(pk__in=self.verified_all())


class VerificationModelManager(VERIFICATION_BASE_MANAGER):

    def available_model_names(self):

        verification_model_names = []
        for field in self.model._meta.fields:
            if "ForeignKey" in str(type(field)) and "user" not in str(field):
                verification_model_names.append(field.name)
        return verification_model_names

    def filter_by_model_name(self, model_name):

        return self.filter(**{"{}__isnull".format(model_name): False})

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
        return model.objects.verified()

    def unverified_objects(self, model_name):

        model = get_model(model_name, app_name=settings.SITE_NAME)
        return model.objects.unverified()

