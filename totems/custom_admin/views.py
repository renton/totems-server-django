from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import simplejson
import os
from totems.models import Client, Totem, TotemMessage, WorldLayer, RequestLog
from random import randrange
from password_required.decorators import password_required

ROWS_PER_PAGE = 100

@password_required
def home(request):
    c = {}
    return render_to_response("custom_admin/base.html",c,context_instance=RequestContext(request))

# ========================================
# --- CLIENTS ---
# ========================================

@password_required
def clients_list(request,sort_param=None):
    
    if sort_param:
        sort_param = sort_param
    else:
        sort_param = "last_activity"

    clients = Client.objects.all().order_by('-'+str(sort_param))

    c = {
        'clients':clients
    }

    for client in clients:
        client.x_num_messages = TotemMessage.get_message_count_by_client(client)
        client.x_num_totems = Totem.get_totem_count_by_client(client)

    return render_to_response("custom_admin/clients/list.html",c,context_instance=RequestContext(request))

@password_required
def clients_registration_map(request):
    clients = Client.objects.all()[:100]
    points = []
    for client in clients:
        points.append({
            "coors":(client.registration_longitude,client.registration_latitude),
            "label":"R",
            "color":"ff776b",
            "message":"",
            "totem_id":"null",
        })

    c = {
        'points':points
    }
    return render_to_response("custom_admin/clients/registration_map.html",c,context_instance=RequestContext(request))

@password_required
def clients_requests_map(request):
    logs = RequestLog.objects.all().order_by('-created')[:100]
    points = []
    for log in logs:
        points.append({
            "coors":(log.longitude,log.latitude),
            "label":"R",
            "color":"ff776b",
            "message":str(log.client.device_id),
            "totem_id":"null",
        })

    c = {
        'points':points
    }
    return render_to_response("custom_admin/base_map.html",c,context_instance=RequestContext(request))

@password_required
def clients_detail(request,ClientID):
    client = Client.objects.get(pk=ClientID)
    totems = Totem.objects.filter(owner=client)
    messages = TotemMessage.objects.filter(owner=client)
    client.x_num_messages = messages.count()
    client.x_num_totems = totems.count()
    requests = RequestLog.objects.filter(client=client)
    client.x_num_requests = len(requests)
    c = {
        'client':client,
        'totems':totems,
        'messages':messages
    }
    return render_to_response("custom_admin/clients/detail.html",c,context_instance=RequestContext(request))

@password_required
def clients_activity_map(request,ClientID=None):
    if ClientID is not None:
        client = Client.objects.get(pk=ClientID)
        messages = TotemMessage.objects.filter(owner=client)
        request_logs = RequestLog.objects.filter(client=client)
    else:
        totems = []
        message = []
        request_logs = []

    points = []
    for log in request_logs:
       points.append({
            "coors":(log.longitude,log.latitude),
            "label":"R",
            "color":"6b77ff",
            "message":"",
            "totem_id":"null",
        })
    for message in messages:
       points.append({
            "coors":(message.totem.longitude,message.totem.latitude),
            "label":"M",
            "color":"ff776b",
            "message":str(message.totem.get_parent_message().message)+" ("+str(message.totem.get_message_count())+")",
            "totem_id":message.totem.id,
        })

    c = {
        'points':points
    }
    return render_to_response("custom_admin/clients/activity_map.html",c,context_instance=RequestContext(request))

# ========================================
# --- TOTEMS ---
# ========================================

@password_required
def totems_list(request):

    totems = Totem.objects.all().order_by('-last_activity')

    c = {
        'totems':totems,
    }
    return render_to_response("custom_admin/totems/list.html",c,context_instance=RequestContext(request))

@password_required
def totems_detail(request,TotemID):

    #TODO proper form
    if request.method == "POST":
        if 'message' in request.POST and 'parent_message_id' in request.POST:
            if request.POST['message'] != "":
                admin, created = Client.get_or_register_client("admin")
                parent = TotemMessage.objects.get(pk=request.POST['parent_message_id'])
                parent.reply_message(request.POST['message'],admin)

    totem = Totem.objects.get(pk=TotemID)
    parent = totem.get_parent_message()
    messages = parent.list_from_node()

    c = {
        'totem':totem,
        'messages':messages
    }

    return render_to_response("custom_admin/totems/detail.html",c,context_instance=RequestContext(request))

@password_required
def totems_map(request):
    totems = Totem.objects.all()
    points = []
    for totem in totems:
        points.append({
            "coors":(totem.longitude,totem.latitude),
            "label":"T",
            "color":"ff776b",
            "message":str(totem.get_parent_message().message)+" ("+str(totem.get_message_count())+")",
            "totem_id":totem.id,
        })
    c = {
        'points':points
    }
    return render_to_response("custom_admin/totems/map.html",c,context_instance=RequestContext(request))

@password_required
def totems_map_single(request,TotemID):
    totem = Totem.objects.get(id=TotemID)
    points = []
    points.append({
        "coors":(totem.longitude,totem.latitude),
        "label":"T",
        "color":"ff776b",
        "message":str(totem.get_parent_message().message)+" ("+str(totem.get_message_count())+")",
        "totem_id":totem.id,
    })
    c = {
        'points':points
    }
    return render_to_response("custom_admin/totems/map_single.html",c,context_instance=RequestContext(request))
    

# ========================================
# --- MESSAGES ---
# ========================================

@password_required
def messages_list(request):
    messages = TotemMessage.objects.all().order_by('-created')
    c = {
        'messages':messages
    }
    return render_to_response("custom_admin/messages/list.html",c,context_instance=RequestContext(request))

@password_required
def messages_list_flags(request):
    raw_messages = TotemMessage.objects.filter(active=True).order_by('-created')
    messages = []

    for raw_message in raw_messages:
        flag_count = raw_message.get_flag_count
        if flag_count > 0:
            raw_message.x_get_flag_count = flag_count
            messages.append(raw_message)

    messages = list(messages)
    messages.sort(key = lambda row: row.x_get_flag_count, reverse=True)

    c = {
        'messages':messages
    }
    return render_to_response("custom_admin/messages/list.html",c,context_instance=RequestContext(request))

@password_required
def ajax_delete_message(request,MessageID):
    msg_to_delete = TotemMessage.objects.get(pk=MessageID)
    msg_to_delete.remove()
    return HttpResponse(simplejson.dumps({'success':True,'message':MessageID}))

# ========================================
# --- SIMULATOR ---
# ========================================

@password_required
def simulate_app(request):

    c = {
        'zoom_override':18,
        'sim_mode':True,
    }

    #TODO proper form
    if request.method == "POST":
        if 'message' in request.POST and 'longitude' in request.POST and 'latitude' in request.POST:
            if request.POST['message'] != "":
                admin, created = Client.get_or_register_client("admin")
                wl1 = WorldLayer.objects.get(id=1)
                Totem.add_totem(admin,request.POST['longitude'],request.POST['latitude'],request.POST['message'],wl1)

    return render_to_response("custom_admin/simulator/map.html",c,context_instance=RequestContext(request))

# ========================================
# --- API TEST ---
# ========================================

@password_required
def apitest_register(request):
    c={}

    c['api_call_name'] = "register"
    c['required_params'] = [
        'device_id',
        'device_name',
        'device_version',
        'device_platform',
        'registration_longitude',
        'registration_latitude',
    ]

    return render_to_response("custom_admin/api_test/base.html",c,context_instance=RequestContext(request))

@password_required
def apitest_add_totem(request):
    c={}

    c['api_call_name'] = "add_totem"
    c['required_params'] = [
        'device_id',
        'longitude',
        'latitude',
        'message',
        'worldlayer_id',
    ]

    return render_to_response("custom_admin/api_test/base.html",c,context_instance=RequestContext(request))

@password_required
def apitest_fetch_totems(request):
    c={}

    c['api_call_name'] = "fetch_totems"
    c['required_params'] = [
        'device_id',
        'longitude',
        'latitude',
        'worldlayer_id',
    ]

    return render_to_response("custom_admin/api_test/base.html",c,context_instance=RequestContext(request))

@password_required
def apitest_add_reply(request):
    c={}

    c['api_call_name'] = "add_reply"
    c['required_params'] = [
        'device_id',
        'parent_message_id',
        'message',
        'worldlayer_id',
    ]

    return render_to_response("custom_admin/api_test/base.html",c,context_instance=RequestContext(request))

@password_required
def apitest_fetch_totem_thread(request):
    c={}

    c['api_call_name'] = "fetch_totem_thread"
    c['required_params'] = [
        'device_id',
        'parent_message_id',
        'depth',
    ]

    return render_to_response("custom_admin/api_test/base.html",c,context_instance=RequestContext(request))

@password_required
def apitest_toggle_flag(request):
    c={}

    c['api_call_name'] = "toggle_flag"
    c['required_params'] = [
        'device_id',
        'message_id',
    ]

    return render_to_response("custom_admin/api_test/base.html",c,context_instance=RequestContext(request))

@password_required
def apitest_fetch_messages(request):
    c={}

    c['api_call_name'] = "fetch_messages"
    c['required_params'] = [
            'device_id',
            'longitude',
            'latitude',
            'worldlayer_id',
            'page',
        ]

    return render_to_response("custom_admin/api_test/base.html",c,context_instance=RequestContext(request))
