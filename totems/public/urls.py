from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'totems.public.views.home', name='public_home'),
)
