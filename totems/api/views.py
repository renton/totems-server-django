from django.http import HttpResponse, Http404
from django.utils import simplejson
from totems.models import Client, Totem, TotemMessage, WorldLayer
from django.views.decorators.csrf import csrf_exempt                                          
from totems.tools import lat_long_distance

TOTEMS_MAX_FETCH_RANGE_LATITUDE = 0.005
TOTEMS_MAX_FETCH_RANGE_LONGITUDE = 0.0025

@csrf_exempt
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

@csrf_exempt
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

@csrf_exempt
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

@csrf_exempt
def fetch_totems(request):

    if request.method == "POST":

        required_params = [
            'device_id',
            'longitude',
            'latitude',
            'worldlayer_id',
        ]

        for param in required_params:
            if param not in request.POST.keys():
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

        latitude = float(request.POST['latitude'])
        longitude = float(request.POST['longitude'])

        lat_low_range = latitude - TOTEMS_MAX_FETCH_RANGE_LATITUDE
        long_low_range = longitude - TOTEMS_MAX_FETCH_RANGE_LONGITUDE

        lat_high_range = latitude + TOTEMS_MAX_FETCH_RANGE_LATITUDE
        long_high_range = longitude + TOTEMS_MAX_FETCH_RANGE_LONGITUDE

        totems = Totem.objects.filter(
            longitude__range=(long_low_range,long_high_range),
            latitude__range=(lat_low_range,lat_high_range),
        )

        output = {}
        output['totems'] = []

        for totem in totems:
            distance = lat_long_distance((latitude,longitude),(totem.latitude,totem.longitude))

            parent_message = totem.get_parent_message()
            output['totems'].append({
                'id':totem.id,
                'message':parent_message.message,
                'message_count':totem.get_message_count(),
                'last_activity':str(totem.last_activity),
                'created':str(totem.created),
                'distance':distance,
            })

        output['total'] = len(output['totems'])
        
        output['success'] = True

        return HttpResponse(simplejson.dumps(output), 'application/json')
    else:
        raise Http404
