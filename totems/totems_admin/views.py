from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import simplejson
import os
from totems.core.models import Client, Totem, TotemMessage, WorldLayer, Mark, RequestLog

def home(request):
    c = {}
    return render_to_response("base.html",c,context_instance=RequestContext(request))

def clients_list(request):
    clients = Client.objects.all().order_by('-last_activity')
    c = {
        'clients':clients
    }

    for client in clients:
        client.x_num_messages = TotemMessage.objects.filter(owner=client).count()
        client.x_num_totems = Totem.objects.filter(owner=client).count()

    return render_to_response("clients/list.html",c,context_instance=RequestContext(request))

def clients_detailed(request,ClientID):
    client = Client.objects.get(pk=ClientID)
    totems = Totem.objects.filter(owner=client)
    messages = TotemMessage.objects.filter(owner=client)
    client.x_num_messages = messages.count()
    client.x_num_totems = totems.count()
    c = {
        'client':client,
        'totems':totems,
        'messages':messages
    }
    return render_to_response("clients/detailed.html",c,context_instance=RequestContext(request))

def clients_activity_map(request,ClientID=None):
    if ClientID is not None:
        client = Client.objects.get(pk=ClientID)
        totems = Totem.objects.filter(owner=client)
    else:
        totems = []
    points = []
    for totem in totems:
        points.append(totem.point)
    c = {
        'points':points
    }
    return render_to_response("clients/activity_map.html",c,context_instance=RequestContext(request))

def clients_registration_map(request):
    clients = Client.objects.all()
    points = []
    for client in clients:
        points.append(client.registration_point)

    c = {
        'points':points
    }
    return render_to_response("clients/map.html",c,context_instance=RequestContext(request))

def logs_list(request):
    logs = RequestLog.objects.all().order_by('-created')
    c = {
        'logs':logs
    }
    return render_to_response("logs/list.html",c,context_instance=RequestContext(request))

def totems_list(request):

    #TODO proper form
    if request.method == "POST":
        if 'message' in request.POST and 'layer' in request.POST:
            if request.POST['message'] != "":
                admin = Client.get_or_register_client("admin")
                layer = WorldLayer.objects.get(name=request.POST['layer'])
                Totem.add_totem(admin,None,request.POST['message'],layer)

    totems = Totem.objects.all().order_by('-last_activity')
    layers = WorldLayer.objects.all()
    c = {
        'totems':totems,
        'layers':layers
    }
    return render_to_response("totems/list.html",c,context_instance=RequestContext(request))

def totems_map(request):
    totems = Totem.objects.all()
    points = []
    for totem in totems:
        points.append(totem.point)
    c = {
        'points':points
    }
    return render_to_response("totems/map.html",c,context_instance=RequestContext(request))
    
def totems_detail(request,TotemID):

    admin = Client.get_or_register_client("admin")
    #TODO proper form
    if request.method == "POST":
        if 'message' in request.POST and 'parent_message_id' in request.POST:
            if request.POST['message'] != "":
                parent = TotemMessage.objects.get(pk=request.POST['parent_message_id'])
                parent.reply_message(request.POST['message'],admin)

    totem = Totem.objects.get(pk=TotemID)
    parent = totem.get_parent_message()
    messages = parent.list_from_node()

    for message in messages:
        message[1].x_num_spam_marks = Mark.get_mark_count_for_message(message[1],Mark.MARK_TYPE_SPAM)
        message[1].x_num_flag_marks = Mark.get_mark_count_for_message(message[1],Mark.MARK_TYPE_REPORT)
        message[1].x_num_vote_marks = Mark.get_mark_count_for_message(message[1],Mark.MARK_TYPE_UPVOTE) - Mark.get_mark_count_for_message(message[1],Mark.MARK_TYPE_DOWNVOTE)
        message[1].x_is_marked_spam = Mark.is_marked_for_client(admin,message[1],Mark.MARK_TYPE_SPAM)
        message[1].x_is_marked_flag = Mark.is_marked_for_client(admin,message[1],Mark.MARK_TYPE_REPORT)
        message[1].x_is_marked_upvote = Mark.is_marked_for_client(admin,message[1],Mark.MARK_TYPE_UPVOTE)
        message[1].x_is_marked_downvote = Mark.is_marked_for_client(admin,message[1],Mark.MARK_TYPE_DOWNVOTE)

    c = {
        'totem':totem,
        'messages':messages
    }
    return render_to_response("totems/detail.html",c,context_instance=RequestContext(request))

def messages_list(request):
    messages = TotemMessage.objects.all().order_by('-created')
    c = {
        'messages':messages
    }
    return render_to_response("messages/list.html",c,context_instance=RequestContext(request))

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

def ajax_delete_message(request,MessageID):
    msg_to_delete = TotemMessage.objects.get(pk=MessageID)
    msg_to_delete.remove()
    return HttpResponse(simplejson.dumps({'success':True,'message':MessageID}))

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
