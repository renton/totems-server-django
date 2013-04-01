from django.conf.urls import patterns, include, url
from password_required.decorators import password_required

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', include('totems.public.urls')),
    url(r'^panel/', include('totems.custom_admin.urls')),
    url(r'^api/', include('totems.api.urls')),
    url(r'^password_required/$', 'password_required.views.login'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^renmin/', include(admin.site.urls)),
)
