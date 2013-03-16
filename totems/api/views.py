from django.http import HttpResponse, Http404
from django.utils import simplejson
from totems.models import Client, Totem, TotemMessage, WorldLayer

def register(request):    

    if request.method == "POST":

        #timestamp,hash,device_id,device_name,device_version,device_platform,reg_long,reg_lat

        required_params = [
            'device_id',
            'device_name',
            'device_version',
            'device_platform',
            'registration_longitude',
            'registration_latitude',
        ]

        for param in required_params:
            if param not in request.POST.keys():
                raise Http404

        registered_client,created = Client.get_or_register_client(
            request.POST['device_id'],
            request.POST['device_name'],
            request.POST['device_version'],
            request.POST['device_platform'],
            request.POST['registration_longitude'],
            request.POST['registration_latitude']
        )

        output = {}

        output['is_banned'] = registered_client.is_banned
        output['is_active'] = registered_client.active
        output['created'] = created

        return HttpResponse(simplejson.dumps(output), 'application/json')
    else:
        raise Http404

def add_totem(request):

    if request.method == "POST":

        required_params = [
            'device_id',
            'longitude',
            'latitude',
            'message',
            'worldlayer_id',
        ]

        for param in required_params:
            if param not in request.POST.keys():
                raise Http404

        # cannot send empty message
        if request.POST['message'] == "":
            raise Http404

        # client must exist in system and be registered
        try:
            client = Client.objects.get(device_id=request.POST['device_id'])
        except:
            raise Http404

        # make sure worldlayer exists
        try:
            worldlayer = WorldLayer.objects.get(id=request.POST['worldlayer_id'])
        except:
            raise Http404

        Totem.add_totem(
            client,
            request.POST['longitude'],
            request.POST['latitude'],
            request.POST['message'],
            worldlayer
        )

        output = {}
        output['success'] = True

        return HttpResponse(simplejson.dumps(output), 'application/json')
    else:
        raise Http404

def add_reply(request):

    if request.method == "POST":

        required_params = [
            'device_id',
            'parent_message_id',
            'message',
        ]

        for param in required_params:
            if param not in request.POST.keys():
                raise Http404

        # cannot send empty message
        if request.POST['message'] == "":
            raise Http404

        # client must exist in system and be registered
        try:
            client = Client.objects.get(device_id=request.POST['device_id'])
        except:
            raise Http404

        # parent message must exist in system and be registered
        try:
            parent_message = TotemMessage.objects.get(id=request.POST['parent_message_id'])
        except:
            raise Http404

        parent_message.reply_message(request.POST['message'],client)

        output = {}
        output['success'] = True

        return HttpResponse(simplejson.dumps(output), 'application/json')
    else:
        raise Http404
