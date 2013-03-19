from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'totems.custom_admin.views.home', name='home'),
    url(r'^clients/$', 'totems.custom_admin.views.clients_list', name='clients_list'),
    url(r'^clients/sort/(?P<sort_param>.+)/$', 'totems.custom_admin.views.clients_list', name='clients_list_sorted'),
    url(r'^clients/detailed/(?P<ClientID>.+)/$', 'totems.custom_admin.views.clients_detail', name='clients_detail'),
    url(r'^clients/activity_map/(?P<ClientID>.+)/$', 'totems.custom_admin.views.clients_activity_map', name='clients_activity_map'),
    url(r'^clients/registration_map/$', 'totems.custom_admin.views.clients_registration_map', name='clients_registration_map'),
    url(r'^totems/$', 'totems.custom_admin.views.totems_list', name='totems_list'),
    url(r'^totems/map_single/(?P<TotemID>.+)/$', 'totems.custom_admin.views.totems_map_single', name='totems_map_single'),
    url(r'^totems/map/$', 'totems.custom_admin.views.totems_map', name='totems_map'),
    url(r'^totems/(?P<TotemID>.+)/$', 'totems.custom_admin.views.totems_detail', name='totems_detail'),
    url(r'^apitest/register/$', 'totems.custom_admin.views.apitest_register', name='apitest_register'),
    url(r'^apitest/add_totem/$', 'totems.custom_admin.views.apitest_add_totem', name='apitest_add_totem'),
    url(r'^apitest/fetch_totems/$', 'totems.custom_admin.views.apitest_fetch_totems', name='apitest_fetch_totems'),
    url(r'^apitest/fetch_messages/$', 'totems.custom_admin.views.apitest_fetch_messages', name='apitest_fetch_messages'),
    url(r'^apitest/fetch_totem_thread/$', 'totems.custom_admin.views.apitest_fetch_totem_thread', name='apitest_fetch_totem_thread'),
    url(r'^apitest/add_reply/$', 'totems.custom_admin.views.apitest_add_reply', name='apitest_add_reply'),
    url(r'^messages/$', 'totems.custom_admin.views.messages_list', name='messages_list'),
    url(r'^messages/delete/(?P<MessageID>.+)/$', 'totems.custom_admin.views.ajax_delete_message'),


    #url(r'^clients/activity_map/$', 'totems.custom_admin.views.clients_activity_map', name='clientsActivityMapEmpty'),
    #url(r'^clients/activity_map/(?P<ClientID>.+)/$', 'totems.custom_admin.views.clients_activity_map', name='clientsActivityMap'),


    #url(r'^messages/mark/spam/(?P<MessageID>.+)/$', 'totems.custom_admin.views.ajax_mark_message_as_spam'),
    #url(r'^messages/mark/flag/(?P<MessageID>.+)/$', 'totems.custom_admin.views.ajax_mark_message_as_flagged'),
    #url(r'^messages/mark/downvote/(?P<MessageID>.+)/$', 'totems.custom_admin.views.ajax_mark_downvote'),
    #url(r'^messages/mark/upvote/(?P<MessageID>.+)/$', 'totems.custom_admin.views.ajax_mark_upvote'),
    #url(r'^logs/$', 'totems.custom_admin.views.logs_list', name='logsList'),
    #url(r'^marks/$', 'totems.custom_admin.views.marks_list', name='marksList'),
    #url(r'^simulate/traffic/$', 'totems.custom_admin.views.simulate_traffic', name='simulateTraffic'),
)
