from django.shortcuts import render_to_response
from django.template import RequestContext
from totems.core.models import Client, Totem, TotemMessage, WorldLayer

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
    
def totems_detail(request,TotemID):

    #TODO proper form
    if request.method == "POST":
        if 'message' in request.POST and 'parent_message_id' in request.POST:
            if request.POST['message'] != "":
                admin = Client.get_or_register_client("admin")
                parent = TotemMessage.objects.get(pk=request.POST['parent_message_id'])
                parent.reply_message(request.POST['message'],admin)

    totem = Totem.objects.get(pk=TotemID)
    parent = totem.get_parent_message()
    messages = parent.list_from_node()
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
