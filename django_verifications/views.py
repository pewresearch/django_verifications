import datetime

from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.conf import settings

from pewtils import is_not_null, decode_text
from pewtils.django import get_model
from pewtils.nlp import decode_text
from pewtils.io import FileHandler

from django_verifications.utils import get_verification_model


@login_required
def home(request):

    Verification = get_verification_model()
    verification_models = []
    for model_name in Verification.objects.available_model_names():
        good = Verification.objects.good_objects(model_name).count()
        bad = Verification.objects.bad_objects(model_name).count()
        incomplete = Verification.objects.incomplete_objects(model_name).count()
        verification_models.append({
            "name": model_name,
            "good": good,
            "bad": bad,
            "incomplete": incomplete
        })
    print verification_models
    return render_to_response('verifications/index.html', {
        "verification_models": verification_models
    }, context_instance=RequestContext(request))


@login_required
def verify(request, model_name, pk=None):

    model = get_model(model_name, app_name=settings.SITE_NAME)
    Verification = get_verification_model()

    prev_id = None
    if request.method == "POST":

        prev_id = request.POST.get("pk")
        obj = model.objects.get(pk=prev_id)
        for field in model._meta.fields_to_verify:
            v = Verification.objects.create_or_update(
                {"user": request.user, "field": field, "{}_id".format(model_name): obj.pk},
                {"timestamp": datetime.datetime.now(), "is_good": eval(request.POST.get(field)), "notes": request.POST.get("{}_notes".format(field))},
                save_nulls=True
            )
            print "Saving {}, {}: {} ({})".format(obj, field, v.is_good, v.pk)

    if not pk:
        incomplete = Verification.objects.incomplete_objects(model_name)
        if incomplete.count() > 0:
            new_obj = incomplete.order_by("?")[0]
        else:
            new_obj = None
    else:
        new_obj = model.objects.get(pk=pk)

    if new_obj:

        obj_data = {"fields_to_verify": [], "verification_metadata_fields": [], "pk": new_obj.pk, "model_name": model_name}
        for field in model._meta.fields_to_verify:
            existing_verifications = Verification.objects\
                .filter(**{"{}_id".format(model_name): new_obj.pk})\
                .filter(user=request.user)\
                .filter(field=field)\
                .order_by("-timestamp")
            note = ""
            existing_value = None
            if existing_verifications.count() > 0:
                note = existing_verifications[0].notes
                existing_value =  str(int(existing_verifications[0].is_good)) if is_not_null(existing_verifications[0].is_good) else None
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


# def view_politicians(request):
#
#     table = PoliticianTable(Politician.objects.all())
#     RequestConfig(request).configure(table)
#     return render(request, 'table.html', {"table": table})


# def view_object(request, model_name, object_id):
#
#     obj = get_model(model_name).objects.filter(pk=object_id).values()[0]
#     related = obj.related_object_counts()
#     for k in related.keys():
#         if k not in obj.keys():
#             obj[k] = related[k]
#     pass


# def view_available_exports(request):
#
#     h = FileHandler("output/queries", use_s3=True)
#     keys = [k for k in h.iterate_path()]
#
#     return render_to_response('view_available_exports.html', {
#         "keys": keys
#     }, context_instance=RequestContext(request))


# def facebook_test(request):
#
#     from logos.utils.io import FileHandler, FacebookAPIHandler
#     fb = FacebookAPIHandler()
#     access_token = fb.access_token
#     h = FileHandler("output/queries/partisan_antipathy", use_s3=True)
#     df = h.read("top_100_expresses_anger_posts_by_party", format="csv")
#     return render_to_response('facebook_post_table.html', {
#         "df": df.to_dict("records")[:1],
#         "access_token": access_token
#     }, context_instance=RequestContext(request))
#
#     # def view_table(request, table_name):
# #
# #     fields = []
# #     for f in get_model(table_name)._meta.get_fields():
# #         field = {
# #             "name": f.model_name,
# #             "help_text": f.help_text,
# #             "available_filters": [
# #                 (None, "equals"),
# #                 (None, "does not equal"),
# #                 (None, "is null"),
# #                 (None, "is not null")
# #             ]
# #         }
# #         if not f.is_relation:
# #             field["related_model"] = None
# #
# #             if type(f).__name__ == "CharField":
# #
# #                 field["available_filters"].extend([
# #                     ("length", "greater than"),
# #                     ("length", "greater than or equal to"),
# #                     ("length", "less than"),
# #                     ("length", "less than or equal to")
# #                 ])
# #
# #             elif type(f).__name__ in ["IntegerField", "FloatField"]:
# #
# #                 field["available_filters"].extend([
# #                     (None, "greater than"),
# #                     (None, "greater than or equal to"),
# #                     (None, "less than"),
# #                     (None, "less than or equal to")
# #                 ])
# #
# #         else:
# #             field["related_model"] = f.related_model.model_name
# #
# #         # elif f.one_to_one or f.many_to_one:
# #         #
# #         #     if f.concrete:
# #         #         # direct fk
# #         #         pass
# #         #     else:
# #         #         # related >>> f.remote_field.name
# #         #         pass
# #         #
# #         # elif f.one_to_many:
# #         #
# #         #     # related >>> f.remote_field.name
# #         #     pass
# #         #
# #         # elif f.many_to_many:
# #         #
# #         #     # m2m
# #         #     pass
