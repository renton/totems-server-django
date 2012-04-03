from django.shortcuts import render_to_response
from django.template import RequestContext
from totems.core.models import Client, Totem

def home(request):
    c = {}
    return render_to_response("base.html",c,context_instance=RequestContext(request))

def clients(request):
    clients = Client.objects.all()
    c = {
        'clients':clients
    }
    return render_to_response("clients/list.html",c,context_instance=RequestContext(request))

def totems(request):
    totems = Totem.objects.all()
    c = {
        'totems':totems
    }
    return render_to_response("totems/list.html",c,context_instance=RequestContext(request))
    
