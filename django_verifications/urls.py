from django.conf.urls import patterns

urlpatterns = patterns('', )

urlpatterns += patterns('django_verifications.views',
    (r'^verify$', 'home'),
    (r'^verify/(?P<model_name>.+)/(?P<pk>[0-9]+)$', 'verify'),
    (r'^verify/(?P<model_name>.+)$', 'verify'),
)