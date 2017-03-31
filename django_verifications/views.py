import datetime

from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings

from pewtils import is_not_null, decode_text
from pewtils.django import get_model
from pewtils.nlp import decode_text
from pewtils.io import FileHandler

from django_verifications.models import Verification


@login_required
def home(request):

    verification_models = []
    for model_name in Verification.objects.available_model_names():
        good = Verification.objects.good_objects(model_name).count()
        bad = Verification.objects.bad_objects(model_name).count()
        unverified = Verification.objects.unverified_objects(model_name).count()
        verification_models.append({
            "name": model_name,
            "good": good,
            "bad": bad,
            "unverified": unverified
        })

    return render(request, 'django_verifications/index.html', {
        "verification_models": verification_models
    })


@login_required
def verify(request, model_name, pk=None):

    model_name = model_name.replace(" ", "_")

    model = get_model(model_name, app_name=settings.SITE_NAME)

    prev_id = None
    if request.method == "POST":

        prev_id = request.POST.get("pk")
        obj = model.objects.get(pk=prev_id)
        for field in model._meta.fields_to_verify:
            v = Verification.objects.create_or_update(
                {"user": request.user, "field": field, "content_object": obj},
                {"timestamp": datetime.datetime.now(), "is_good": eval(request.POST.get(field)), "notes": request.POST.get("{}_notes".format(field))},
                save_nulls=True
            )
            print "Saving {}, {}: {} ({})".format(obj, field, v.is_good, v.pk)

    if not pk:
        unverified = Verification.objects.unverified_objects(model_name)
        if unverified.count() > 0:
            new_obj = unverified.order_by("?")[0]
        else:
            new_obj = None
    else:
        new_obj = model.objects.get(pk=pk)

    if new_obj:

        obj_data = {"fields_to_verify": [], "pk": new_obj.pk, "model_name": model_name}
        for field in model._meta.fields_to_verify:
            existing_verifications = Verification.objects\
                .filter(**{model_name: new_obj})\
                .filter(user=request.user)\
                .filter(field=field)\
                .order_by("-timestamp")
            note = ""
            existing_value = None
            if existing_verifications.count() > 0:
                note = existing_verifications[0].notes
                existing_value =  str(int(existing_verifications[0].is_good)) if is_not_null(existing_verifications[0].is_good) else None

            obj_data["fields_to_verify"].append((field, decode_text(getattr(new_obj, field)), existing_value, note))

        obj_data["verification_metadata"] = new_obj.get_verification_metadata()

        obj_data["prev_id"] = prev_id

        return render(request, 'django_verifications/verify.html', obj_data)

    else:

        return home(request)


@login_required
def correct(request, model_name, pk=None):

    model_name = model_name.replace(" ", "_")

    model = get_model(model_name, app_name=settings.SITE_NAME)

    prev_id = None
    if request.method == "POST":

        prev_id = request.POST.get("pk")
        obj = model.objects.get(pk=prev_id)
        for field in model._meta.fields_to_verify:
            raise Exception("Feature not yet implemented")
            # v = Verification.objects.get_if_exists({"user": request.user, "field": field, "content_object": obj})
            # if not v.is_good:
            #     setattr(obj, field, request.POST.get(field))
            #     obj.save()
            #     v.timestamp = datetime.datetime.now()
            #     v.is_good = True
            #     v.save()
            #     print "Saving {}, {}: {} ({})".format(obj, field, v.is_good, v.pk)

    if not pk:
        bad = Verification.objects.bad_objects(model_name)
        if bad.count() > 0:
            new_obj = bad.order_by("?")[0]
        else:
            new_obj = None
    else:
        new_obj = model.objects.get(pk=pk)

    if new_obj:

        obj_data = {"fields_to_verify": [], "pk": new_obj.pk, "model_name": model_name}
        for field in model._meta.fields_to_verify:
            existing_verifications = Verification.objects\
                .filter(**{model_name: new_obj})\
                .filter(user=request.user)\
                .filter(field=field)\
                .order_by("-timestamp")
            note = ""
            existing_value = None
            if existing_verifications.count() > 0:
                note = existing_verifications[0].notes
                existing_value =  str(int(existing_verifications[0].is_good)) if is_not_null(existing_verifications[0].is_good) else None

            obj_data["fields_to_verify"].append((field, decode_text(getattr(new_obj, field)), existing_value, note))

            obj_data["verification_metadata"] = new_obj.get_verification_metadata()

        obj_data["prev_id"] = prev_id

        return render(request, 'django_verifications/correct.html', obj_data)

    else:

        return home(request)
