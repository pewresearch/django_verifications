# import pandas, re
#
# from django.apps import apps
#
# from django_pewtils import get_model
#
# from django_verifications.models import Verification
#
#
# def get_verification_dataframe(model_name):
#
#     model = get_model(model_name)
#     verified_objects = Verification.objects.verified_objects()
#     verifications = Verification.objects.verified()
#
#     verif_fields = ["pk", model_name, "field", "user", "timestamp", "is_good", "notes"]
#     verifications = pandas.DataFrame.from_records(verifications.values(*verif_fields))
#
#     obj_fields = ["pk"] + \
#                  model._meta.verification_metadata_fields + \
#                  model._meta.fields_to_verify
#     verified_objects = pandas.DataFrame.from_records(verified_objects.values(*obj_fields))
#
#     verifications = verifications.merge(verified_objects, how="left", left_on="{}_id".format(model_name), right_on="pk", suffixes=('', '_obj'))
#     verifications["field_value"] = verifications.apply(lambda x: x["{}_obj".format(x["field"])], axis=1)
#     for f in model._meta.verification_metadata_fields:
#         del verifications["{}_obj".format(f)]
#
#     return verifications
