# Create your views here.
from django.http import HttpResponse
from django.utils import simplejson
from totems.core.models import TotemMessage

def test(request):
    msgs = TotemMessage.objects.filter()
    output = []
    for msg in msgs:
        msg_data = {}
        msg_data['created'] = str(msg.created)
        msg_data['message'] = msg.message
        msg_data['is_active'] = msg.active
        output.append(msg_data)
    return HttpResponse(simplejson.dumps({'messages':output}))
