from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

def home(request):
    c = {}
    return render_to_response("public/home.html",c,context_instance=RequestContext(request))
