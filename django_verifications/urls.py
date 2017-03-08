from django.conf.urls import url

from django_verifications import views


app_name = 'django_verifications'
urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^(?P<model_name>.+)/(?P<pk>[0-9]+)$', views.verify, name="verify"),
    url(r'^(?P<model_name>.+)$', views.verify, name="verify"),
]