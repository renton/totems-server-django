from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'totems.totems_admin.views.home', name='home'),
    url(r'^clients/$', 'totems.totems_admin.views.clients', name='clients'),
    url(r'^totems/', 'totems.totems_admin.views.totems', name='totems'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
