from django.conf.urls import url

from django_verifications import views


app_name = "django_verifications"
urlpatterns = [
    url(r"^$", views.home, name="home"),
    url(r"^verify/(?P<model_name>.+)/(?P<pk>[0-9]+)$", views.verify, name="verify"),
    url(r"^verify/(?P<model_name>.+)$", views.verify, name="verify"),
    url(
        r"^set_as_incorrect/(?P<model_name>.+)/(?P<pk>[0-9]+)/(?P<field>.+)$",
        views.set_as_incorrect,
        name="set_as_incorrect",
    ),
    url(r"^correct/(?P<model_name>.+)/(?P<pk>[0-9]+)$", views.correct, name="correct"),
    url(r"^correct/(?P<model_name>.+)$", views.correct, name="correct"),
]
