from django.urls import re_path
from django_verifications import views


app_name = "django_verifications"
urlpatterns = [
    re_path(r"^$", views.home, name="home"),
    re_path(r"^verify/(?P<model_name>.+)/(?P<pk>[0-9]+)$", views.verify, name="verify"),
    re_path(r"^verify/(?P<model_name>.+)$", views.verify, name="verify"),
    re_path(
        r"^set_as_incorrect/(?P<model_name>.+)/(?P<pk>[0-9]+)/(?P<field>.+)$",
        views.set_as_incorrect,
        name="set_as_incorrect",
    ),
    re_path(
        r"^correct/(?P<model_name>.+)/(?P<pk>[0-9]+)$", views.correct, name="correct"
    ),
    re_path(r"^correct/(?P<model_name>.+)$", views.correct, name="correct"),
]
