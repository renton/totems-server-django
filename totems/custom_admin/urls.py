from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'totems.custom_admin.views.home', name='home'),
    url(r'^clients/$', 'totems.custom_admin.views.clients_list', name='clientsList'),
    url(r'^clients/registration_map/$', 'totems.custom_admin.views.clients_registration_map', name='clientsRegistrationMap'),
    url(r'^clients/detailed/(?P<ClientID>.+)/$', 'totems.custom_admin.views.clients_detailed', name='clientsDetailed'),
    url(r'^clients/activity_map/$', 'totems.custom_admin.views.clients_activity_map', name='clientsActivityMapEmpty'),
    url(r'^clients/activity_map/(?P<ClientID>.+)/$', 'totems.custom_admin.views.clients_activity_map', name='clientsActivityMap'),
    url(r'^totems/$', 'totems.custom_admin.views.totems_list', name='totemsList'),
    url(r'^totems/map/$', 'totems.custom_admin.views.totems_map', name='totemsMap'),
    url(r'^totems/(?P<TotemID>.+)/$', 'totems.custom_admin.views.totems_detail', name='totemsDetail'),
    url(r'^messages/$', 'totems.custom_admin.views.messages_list', name='messagesList'),
    url(r'^messages/delete/(?P<MessageID>.+)/$', 'totems.custom_admin.views.ajax_delete_message'),
    url(r'^messages/mark/spam/(?P<MessageID>.+)/$', 'totems.custom_admin.views.ajax_mark_message_as_spam'),
    url(r'^messages/mark/flag/(?P<MessageID>.+)/$', 'totems.custom_admin.views.ajax_mark_message_as_flagged'),
    url(r'^messages/mark/downvote/(?P<MessageID>.+)/$', 'totems.custom_admin.views.ajax_mark_downvote'),
    url(r'^messages/mark/upvote/(?P<MessageID>.+)/$', 'totems.custom_admin.views.ajax_mark_upvote'),
    url(r'^logs/$', 'totems.custom_admin.views.logs_list', name='logsList'),
    url(r'^marks/$', 'totems.custom_admin.views.marks_list', name='marksList'),
    url(r'^simulate/traffic/$', 'totems.custom_admin.views.simulate_traffic', name='simulateTraffic'),
)
