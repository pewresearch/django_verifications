from django.apps import apps

from django_verifications.models import VerificationModel


def get_verification_model():

    verification_models = []
    for app, model_list in apps.all_models.iteritems():
        for model_name, model in model_list.iteritems():
            if model.__base__ == VerificationModel:
                verification_models.append(model)

    if len(verification_models) == 1:
        return verification_models[0]
    else:
        raise Exception("You need one and only one verification model, we found: {}".format(verification_models))

