from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import simplejson
import os
from totems.models import Client, Totem, TotemMessage, WorldLayer, RequestLog
from random import randrange

ROWS_PER_PAGE = 100

def home(request):
    c = {}
    return render_to_response("custom_admin/base.html",c,context_instance=RequestContext(request))

# ========================================
# --- CLIENTS ---
# ========================================

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

def clients_registration_map(request):
    clients = Client.objects.all()
    points = []
    for client in clients:
        points.append({
            "coors":(client.registration_longitude,client.registration_latitude),
            "label":"R",
            "color":"ff776b",
            "message":"",
        })

    c = {
        'points':points
    }
    return render_to_response("custom_admin/clients/registration_map.html",c,context_instance=RequestContext(request))

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
    for message in messages:
       points.append({
            "coors":(message.totem.longitude,message.totem.latitude),
            "label":"M",
            "color":"ff776b",
            "message":message.totem.get_parent_message().message,
            "totem_id":message.totem.id,
        })
    for log in request_logs:
       points.append({
            "coors":(log.longitude,log.latitude),
            "label":"R",
            "color":"6b77ff",
            "message":"",
        })

    c = {
        'points':points
    }
    return render_to_response("custom_admin/clients/activity_map.html",c,context_instance=RequestContext(request))

# ========================================
# --- TOTEMS ---
# ========================================

def totems_list(request):

    totems = Totem.objects.all().order_by('-last_activity')

    c = {
        'totems':totems,
    }
    return render_to_response("custom_admin/totems/list.html",c,context_instance=RequestContext(request))

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

def totems_map(request):
    totems = Totem.objects.all()
    points = []
    for totem in totems:
        points.append({
            "coors":(totem.longitude,totem.latitude),
            "label":"T",
            "color":"ff776b",
            "message":totem.get_parent_message().message,
            "totem_id":totem.id,
        })
    c = {
        'points':points
    }
    return render_to_response("custom_admin/totems/map.html",c,context_instance=RequestContext(request))

def totems_map_single(request,TotemID):
    totem = Totem.objects.get(id=TotemID)
    points = []
    points.append({
        "coors":(totem.longitude,totem.latitude),
        "label":"T",
        "color":"ff776b",
        "message":totem.get_parent_message().message,
        "totem_id":totem.id,
    })
    c = {
        'points':points
    }
    return render_to_response("custom_admin/totems/map_single.html",c,context_instance=RequestContext(request))
    

# ========================================
# --- MESSAGES ---
# ========================================

def messages_list(request):
    messages = TotemMessage.objects.all().order_by('-created')
    c = {
        'messages':messages
    }
    return render_to_response("custom_admin/messages/list.html",c,context_instance=RequestContext(request))

def ajax_delete_message(request,MessageID):
    msg_to_delete = TotemMessage.objects.get(pk=MessageID)
    msg_to_delete.remove()
    return HttpResponse(simplejson.dumps({'success':True,'message':MessageID}))

# ========================================
# --- API TEST ---
# ========================================

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

def apitest_fetch_totem_thread(request):
    c={}

    c['api_call_name'] = "fetch_totem_thread"
    c['required_params'] = [
        'device_id',
        'totem_id',
        'depth',
    ]

    return render_to_response("custom_admin/api_test/base.html",c,context_instance=RequestContext(request))

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



'''
def logs_list(request):
    logs = RequestLog.objects.all().order_by('-created')
    c = {
        'logs':logs
    }
    return render_to_response("logs/list.html",c,context_instance=RequestContext(request))




    




def marks_list(request):
    marks = Mark.objects.all().order_by('-created')
    c = {
        'marks':marks
    }
    return render_to_response("marks/list.html",c,context_instance=RequestContext(request))

def simulate_traffic(request):
    new_clients = []
    for i in range(0,10):
        c = Client.get_or_register_client(os.urandom(16).encode('hex'))
        new_clients.append(c)

    new_totems = []
    for client in new_clients:
        for j in range(0,10):
            t = Totem.add_totem(client,Client.create_random_point(),os.urandom(16).encode('hex'),WorldLayer.objects.get())
            new_totems.append(t)

    for client in new_clients:
        for totem in new_totems:
            totem.get_parent_message().reply_message(os.urandom(16).encode('hex'),client)

    c={}
    return render_to_response("clients/list.html",c,context_instance=RequestContext(request))



def ajax_mark_message_as_spam(request,MessageID):
    msg_to_mark = TotemMessage.objects.get(pk=MessageID)
    spam_mark = Mark.create_or_toggle_mark(Client.get_or_register_client("admin"),msg_to_mark,Mark.MARK_TYPE_SPAM)
    return HttpResponse(simplejson.dumps({'success':True,'state':spam_mark.state}))

def ajax_mark_message_as_flagged(request,MessageID):
    msg_to_mark = TotemMessage.objects.get(pk=MessageID)
    flag_mark = Mark.create_or_toggle_mark(Client.get_or_register_client("admin"),msg_to_mark,Mark.MARK_TYPE_REPORT)
    return HttpResponse(simplejson.dumps({'success':True,'state':flag_mark.state}))

def ajax_mark_upvote(request,MessageID):
    msg_to_mark = TotemMessage.objects.get(pk=MessageID)
    vote_mark = Mark.create_or_toggle_mark(Client.get_or_register_client("admin"),msg_to_mark,Mark.MARK_TYPE_UPVOTE)
    return HttpResponse(simplejson.dumps({'success':True,'state':vote_mark.state}))

def ajax_mark_downvote(request,MessageID):
    msg_to_mark = TotemMessage.objects.get(pk=MessageID)
    vote_mark = Mark.create_or_toggle_mark(Client.get_or_register_client("admin"),msg_to_mark,Mark.MARK_TYPE_DOWNVOTE)
    return HttpResponse(simplejson.dumps({'success':True,'state':vote_mark.state}))
'''
