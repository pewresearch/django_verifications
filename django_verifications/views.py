import datetime

from django.shortcuts import render_to_response, render
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
    print verification_models
    return render_to_response('verifications/index.html', {
        "verification_models": verification_models
    }, context_instance=RequestContext(request))


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

        obj_data = {"fields_to_verify": [], "verification_metadata_fields": [], "pk": new_obj.pk, "model_name": model_name}
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
            # TODO: this is logos-specific functionality and needs to be removed
            # maybe you allow for a custom function like _get_verification_metadata on the model that can get called
            if field == "politician":
                latest_term = getattr(new_obj, field).latest_term
                if not latest_term:
                    campaigns = getattr(new_obj, field).campaigns.order_by("-election__year")
                    if campaigns.count() > 0:
                        pol_text = " --- latest campaign: {}".format(str(campaigns[0]))
                    else:
                        pol_text = " --- NO TERMS OR CAMPAIGNS FOUND"
                else:
                    pol_text = " --- latest term: {}".format(str(latest_term))
                obj_data["fields_to_verify"].append(
                    (
                        field,
                        decode_text(getattr(new_obj, field)) + pol_text,
                        existing_value,
                        note
                    )
                )
            else:
                obj_data["fields_to_verify"].append((field, decode_text(getattr(new_obj, field)), existing_value, note))

        values = model.objects.filter(pk=new_obj.pk).values(*model._meta.verification_metadata_fields)[0]
        for field in model._meta.verification_metadata_fields:
            try: better_val = decode_text(getattr(new_obj, field))
            except: better_val = decode_text(values.get(field, None))
            obj_data["verification_metadata_fields"].append((field, better_val))

        obj_data["prev_id"] = prev_id

        return render_to_response('verifications/verify.html', obj_data,
                                  context_instance=RequestContext(request))

    else:

        return home(request)
