from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^register/$', 'totems.api.views.register', name='register'),
    url(r'^add_totem/$', 'totems.api.views.add_totem', name='add_totem'),
    url(r'^add_reply/$', 'totems.api.views.add_reply', name='add_reply'),
)
