import pandas

from django.conf import settings

from pewtils.django import get_model

from django_verifications.settings import VERIFICATION_FIELDS, VERIFICATION_BASE_MODEL, VERIFICATION_BASE_MANAGER


class VerificationManager(VERIFICATION_BASE_MANAGER):

    def good_objects(self, model_name):

        model = get_model(model_name, app_name=settings.SITE_NAME)

        df = pandas.DataFrame.from_records(self.filter_by_model_name(model_name).values("{}_id".format(model_name), "field", "is_good"))
        if len(df) > 0:
            good_df = df[df['is_good']==True].groupby("{}_id".format(model_name)).agg(lambda x: len(x.unique()))
            good_df = good_df[good_df['field'] == len(model._meta.fields_to_verify)]
            return model.objects.filter(**{"pk__in": good_df.index})
        else:
            return model.objects.none()

    def good(self, model_name):

        return self.filter(**{"{}_id__in".format(model_name): self.good_objects().values_list("pk", flat=True)})

    def bad_objects(self, model_name):

        model = get_model(model_name, app_name=settings.SITE_NAME)

        df = pandas.DataFrame.from_records(self.filter_by_model_name(model_name).values("{}_id".format(model_name), "field", "is_good"))
        if len(df) > 0:
            bad_df = df[df['is_good'] == False].groupby("{}_id".format(model_name)).agg(lambda x: len(x.unique()))
            bad_df = bad_df[bad_df['field'] > 0]
            return model.objects.filter(**{"pk__in": bad_df.index})
        else:
            return model.objects.none()

    def bad(self, model_name):

        return self.filter(**{"{}_id__in".format(model_name): self.bad_objects().values_list("pk", flat=True)})

    def incomplete_objects(self, model_name):

        df = pandas.DataFrame.from_records(self.filter_by_model_name(model_name).values("{}_id".format(model_name), "field", "is_good"))
        incomplete = self.verifiable_objects(model_name).exclude(**{"pk__in": self.good_objects(model_name)})
        incomplete = incomplete.exclude(**{"pk__in": self.bad_objects(model_name)})

        return incomplete

    def filter_by_model_name(self, model_name):

        return self.filter(**{"{}__isnull".format(model_name): False})

    def verifiable_objects(self, model_name):

        model = get_model(model_name, app_name=settings.SITE_NAME)
        verifiable = model.objects.all()
        for filter in model._meta.verification_filters:
            verifiable = verifiable.filter(**filter)

        return verifiable

    def available_model_names(self):

        verification_model_names = []
        for field in self.model._meta.fields:
            if "ForeignKey" in str(type(field)) and "user" not in str(field):
                verification_model_names.append(field.name)
        return verification_model_names