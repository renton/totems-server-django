from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, Http404

def home(request):
    raise Http404
