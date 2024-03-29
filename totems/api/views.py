from django.http import HttpResponse, Http404
from django.utils import simplejson
from totems.models import Client, Totem, TotemMessage, WorldLayer, RequestLog, Mark
from django.views.decorators.csrf import csrf_exempt                                          
from totems.tools import lat_long_distance, pretty_date
from totems import settings
import time
import hashlib

TOTEMS_MAX_FETCH_RANGE_LATITUDE = 0.002
TOTEMS_MAX_FETCH_RANGE_LONGITUDE = 0.002

MAX_MESSAGES_PER_PAGE = 10


#TODO
# - pagination + limiting?
# time limit for client requests?
# timestamp age + timezones?
# encryption of sensitive fields?

# ===========================================
# ----- REGISTER -----
# ===========================================

@csrf_exempt
def register(request):    

    if request.method == "POST":

        output = {}

        required_params = [
            'device_id',
            'device_name',
            'device_version',
            'device_platform',
            'registration_longitude',
            'registration_latitude',
            'timestamp',
            'secret',
        ]

        # all parameters must be sent
        for param in required_params:
            if param not in request.POST.keys():
                output['success'] = False
                output['alert'] = "missing parameters"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # device id must be non-empty
        if request.POST['device_id'] == "":
                output['success'] = False
                output['alert'] = "empty device id"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # decrypt sensitive fields
        # request.POST['device_id'] = decrypt(request.POST['device_id'])
        # request.POST['registration_longitude'] = decrypt(request.POST['registration_longitude'])
        # request.POST['registration_latitude'] = decrypt(request.POST['registration_latitude'])

        # authorize secret
        if _auth_secret([
                            request.POST['device_id'],
                            request.POST['registration_longitude'],
                            request.POST['registration_latitude'],
                            request.POST['timestamp']], request.POST['secret']) == False:

                output['success'] = False
                output['alert'] = "malformed request"
                return HttpResponse(simplejson.dumps(output), 'application/json')


        try:
            reg_latitude = float(request.POST['registration_latitude'])
            reg_longitude = float(request.POST['registration_longitude'])
        except:
            output['success'] = False
            output['alert'] = "malformed long/lat"
            output['data'] = request.POST['registration_longitude']
            return HttpResponse(simplejson.dumps(output), 'application/json')

        registered_client,created = Client.get_or_register_client(
            request.POST['device_id'],
            request.POST['device_name'],
            request.POST['device_platform'],
            request.POST['device_version'],
            reg_longitude,
            reg_latitude,
        )

        # REPLY NOTIFICATIONS
        output['reply_notifications'] = []
        output['show_notification_alert'] = False
        notifications = TotemMessage.get_all_reply_notifications_for_client(registered_client)
        for notification in notifications:
            if notification.reply_notification_read == False:
                notification.view_reply_notification()
                output['show_notification_alert'] = True
            output['reply_notifications'].append({'id':notification.id,'longitude':notification.totem.longitude,'latitude':notification.totem.latitude})

        output['is_banned'] = registered_client.is_banned
        output['is_active'] = registered_client.active
        output['created'] = created
        output['success'] = True

        print output
        return HttpResponse(simplejson.dumps(output), 'application/json')
    else:
        raise Http404

# ===========================================
# ----- ADD_TOTEM -----
# ===========================================

@csrf_exempt
def add_totem(request):

    if request.method == "POST":

        output = {}

        required_params = [
            'device_id',
            'longitude',
            'latitude',
            'message',
            'worldlayer_id',
            'timestamp',
            'secret',
        ]

        # all parameters must be sent
        for param in required_params:
            if param not in request.POST.keys():
                output['success'] = False
                output['alert'] = "missing parameters"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # device id must be non-empty
        if request.POST['device_id'] == "":
                output['success'] = False
                output['alert'] = "empty device id"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # cannot send empty message
        if request.POST['message'] == "":
            output['success'] = False
            output['alert'] = "empty message"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        # authorize secret
        if _auth_secret([
                            request.POST['device_id'],
                            request.POST['longitude'],
                            request.POST['latitude'],
                            request.POST['timestamp']], request.POST['secret']) == False:

                output['success'] = False
                output['alert'] = "malformed request"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # client must exist in system and be registered
        try:
            client = Client.objects.get(device_id=request.POST['device_id'])
        except:
            output['success'] = False
            output['alert'] = "unknown client"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        # make sure worldlayer exists
        try:
            worldlayer = WorldLayer.objects.get(id=request.POST['worldlayer_id'])
        except:
            output['success'] = False
            output['alert'] = "unknown world layer"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        Totem.add_totem(
            client,
            request.POST['longitude'],
            request.POST['latitude'],
            request.POST['message'],
            worldlayer
        )

        output['success'] = True

        print output
        return HttpResponse(simplejson.dumps(output), 'application/json')
    else:
        raise Http404

# ===========================================
# ----- ADD_REPLY -----
# ===========================================

@csrf_exempt
def add_reply(request):

    if request.method == "POST":

        output = {}

        required_params = [
            'device_id',
            'parent_message_id',
            'message',
            'timestamp',
            'secret',
        ]

        # all parameters must be sent
        for param in required_params:
            if param not in request.POST.keys():
                output['success'] = False
                output['alert'] = "missing parameters"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # device id must be non-empty
        if request.POST['device_id'] == "":
                output['success'] = False
                output['alert'] = "empty device id"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # cannot send empty message
        if request.POST['message'] == "":
            output['success'] = False
            output['alert'] = "empty message"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        # authorize secret
        if _auth_secret([
                            request.POST['device_id'],
                            request.POST['parent_message_id'],
                            request.POST['timestamp']], request.POST['secret']) == False:

                output['success'] = False
                output['alert'] = "malformed request"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # client must exist in system and be registered
        try:
            client = Client.objects.get(device_id=request.POST['device_id'])
        except:
            output['success'] = False
            output['alert'] = "unknown client"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        # parent message must exist in system and be registered
        try:
            parent_message = TotemMessage.objects.get(id=request.POST['parent_message_id'])
        except:
            output['success'] = False
            output['alert'] = "unknown parent message"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        parent_message.reply_message(request.POST['message'],client)


        output['success'] = True

        print output
        return HttpResponse(simplejson.dumps(output), 'application/json')
    else:
        raise Http404

# ===========================================
# ----- FETCH_TOTEMS -----
# ===========================================

@csrf_exempt
def fetch_totems(request):

    if request.method == "POST":

        output = {}

        required_params = [
            'device_id',
            'longitude',
            'latitude',
            'worldlayer_id',
            'timestamp',
            'secret',
        ]

        # all parameters must be sent
        for param in required_params:
            if param not in request.POST.keys():
                output['success'] = False
                output['alert'] = "missing parameters"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # device id must be non-empty
        if request.POST['device_id'] == "":
                output['success'] = False
                output['alert'] = "empty device id"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # authorize secret
        if _auth_secret([
                            request.POST['device_id'],
                            request.POST['longitude'],
                            request.POST['latitude'],
                            request.POST['timestamp']], request.POST['secret']) == False:

                output['success'] = False
                output['alert'] = "malformed request"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # client must exist in system and be registered
        try:
            client = Client.objects.get(device_id=request.POST['device_id'])
        except:
            output['success'] = False
            output['alert'] = "unknown client"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        # make sure worldlayer exists
        try:
            worldlayer = WorldLayer.objects.get(id=request.POST['worldlayer_id'])
        except:
            output['success'] = False
            output['alert'] = "unknown world layer"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        try:
            latitude = float(request.POST['latitude'])
            longitude = float(request.POST['longitude'])
        except:
            output['success'] = False
            output['alert'] = "malformed long/lat"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        lat_low_range = latitude - TOTEMS_MAX_FETCH_RANGE_LATITUDE
        long_low_range = longitude - TOTEMS_MAX_FETCH_RANGE_LONGITUDE

        lat_high_range = latitude + TOTEMS_MAX_FETCH_RANGE_LATITUDE
        long_high_range = longitude + TOTEMS_MAX_FETCH_RANGE_LONGITUDE

        totems = Totem.objects.filter(
            longitude__range=(long_low_range,long_high_range),
            latitude__range=(lat_low_range,lat_high_range),
            active=True,
        )

        output['totems'] = []

        for totem in totems:
            distance = lat_long_distance((latitude,longitude),(totem.latitude,totem.longitude))*1000
            distance = "%.2f" % distance
            caller_owns = (totem.owner.device_id == request.POST['device_id'])
            timestamp_created = time.mktime(totem.created.timetuple())
            timestamp_last_activity = time.mktime(totem.last_activity.timetuple())

            parent_message = totem.get_parent_message()
            # don't pass content of inactive messages
            if parent_message.active == True:
                message_text = parent_message.message
            else:
                message_text = ""

            output['totems'].append({
                'id':totem.id,
                'message':message_text,
                'message_count':totem.get_message_count(),
                'last_activity':str(totem.last_activity),
                'created':str(totem.created),
                'last_activity_pretty':pretty_date(int(timestamp_last_activity)),
                'created_pretty':pretty_date(int(timestamp_created)),
                'distance':distance,
                'is_owner':caller_owns,
                'longitude':totem.longitude,
                'latitude':totem.latitude,
            })

        output['total'] = len(output['totems'])
        
        # REPLY NOTIFICATIONS
        output['new_reply_notifications'] = []
        output['show_notification_alert'] = False
        notifications = TotemMessage.get_all_unread_reply_notifications_for_client(client)
        for notification in notifications:
            notification.view_reply_notification()
            output['new_reply_notifications'].append({'id':notification.id,'longitude':notification.totem.longitude,'latitude':notification.totem.latitude})
            output['show_notification_alert'] = True

        output['success'] = True

        RequestLog.add_request_log(client,longitude,latitude)
        client.save()

        print output
        return HttpResponse(simplejson.dumps(output), 'application/json')
    else:
        raise Http404

# ===========================================
# ----- FETCH_TOTEM_THREAD -----
# ===========================================

@csrf_exempt
def fetch_totem_thread(request):

    if request.method == "POST":

        output = {}

        required_params = [
            'device_id',
            'parent_message_id',
            'depth',
            'timestamp',
            'secret',
        ]

        # all parameters must be sent
        for param in required_params:
            if param not in request.POST.keys():
                output['success'] = False
                output['alert'] = "missing parameters"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # device id must be non-empty
        if request.POST['device_id'] == "":
                output['success'] = False
                output['alert'] = "empty device id"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # authorize secret
        if _auth_secret([
                            request.POST['device_id'],
                            request.POST['parent_message_id'],
                            request.POST['timestamp']], request.POST['secret']) == False:

                output['success'] = False
                output['alert'] = "malformed request"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # client must exist in system and be registered
        try:
            client = Client.objects.get(device_id=request.POST['device_id'])
        except:
            output['success'] = False
            output['alert'] = "unknown client"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        # totem must exist in system
        try:
            parent_message = TotemMessage.objects.get(id=request.POST['parent_message_id'])
        except:
            output['success'] = False
            output['alert'] = "unknown parent message"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        messages = parent_message.build_message_tree_from_node(request.POST['device_id'],int(request.POST['depth']))

        output['messages'] = messages

        output['success'] = True
        print output

        return HttpResponse(simplejson.dumps(output), 'application/json')
    else:
        raise Http404

# ===========================================
# ----- FETCH_MESSAGES -----
# ===========================================

@csrf_exempt
def fetch_messages(request):

    if request.method == "POST":

        output = {}

        required_params = [
            'device_id',
            'longitude',
            'latitude',
            'worldlayer_id',
            'page',
            'timestamp',
            'secret',
        ]

        print request.POST

        # all parameters must be sent
        for param in required_params:
            if param not in request.POST.keys():
                output['success'] = False
                output['alert'] = "missing parameters"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # device id must be non-empty
        if request.POST['device_id'] == "":
                output['success'] = False
                output['alert'] = "empty device id"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # authorize secret
        if _auth_secret([
                            request.POST['device_id'],
                            request.POST['longitude'],
                            request.POST['latitude'],
                            request.POST['timestamp']], request.POST['secret']) == False:

                output['success'] = False
                output['alert'] = "malformed request"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # client must exist in system and be registered
        try:
            client = Client.objects.get(device_id=request.POST['device_id'])
        except:
            output['success'] = False
            output['alert'] = "unknown client"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        # make sure worldlayer exists
        try:
            worldlayer = WorldLayer.objects.get(id=request.POST['worldlayer_id'])
        except:
            output['success'] = False
            output['alert'] = "unknown world layer"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        try:
            latitude = float(request.POST['latitude'])
            longitude = float(request.POST['longitude'])
        except:
            output['success'] = False
            output['alert'] = "malformed long/lat"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        lat_low_range = latitude - TOTEMS_MAX_FETCH_RANGE_LATITUDE
        long_low_range = longitude - TOTEMS_MAX_FETCH_RANGE_LONGITUDE

        lat_high_range = latitude + TOTEMS_MAX_FETCH_RANGE_LATITUDE
        long_high_range = longitude + TOTEMS_MAX_FETCH_RANGE_LONGITUDE

        messages = TotemMessage.objects.filter(
            totem__longitude__range=(long_low_range,long_high_range),
            totem__latitude__range=(lat_low_range,lat_high_range),
            totem__active=True,
        ).order_by('-created')[
            (int(request.POST['page'])*MAX_MESSAGES_PER_PAGE):
            ((int(request.POST['page'])*MAX_MESSAGES_PER_PAGE)+MAX_MESSAGES_PER_PAGE)
        ]

        output['messages'] = []

        for message in messages:
            distance = lat_long_distance((latitude,longitude),(message.totem.latitude,message.totem.longitude))*1000
            distance = "%.2f" % distance
            caller_owns = (message.owner.device_id == request.POST['device_id'])
            is_parent_totem_message = (message.parent_message == None) 
            timestamp = time.mktime(message.created.timetuple())


            # SET REPLY NOTIFICATIONS AS READ
            #if message.parent_message.owner == client:
                #message.view_reply_notification_replies()

            if message.active == True:
                message_text = message.message
            else:
                message_text = ""

            output['messages'].append({
                'id':message.id,
                'message':message_text,
                'message_count':message.totem.get_message_count(),
                'created':str(message.created),
                'created_pretty':pretty_date(int(timestamp)),
                'distance':distance,
                'is_owner':caller_owns,
                'is_totem_head':is_parent_totem_message,
                'totem_id':message.totem.id,
                'num_replies':message.get_num_replies(),
                'active':message.active,
            })

        output['total'] = len(output['messages'])

        # REPLY NOTIFICATIONS
        output['new_reply_notifications'] = []
        output['show_notification_alert'] = False
        notifications = TotemMessage.get_all_unread_reply_notifications_for_client(client)
        for notification in notifications:
            notification.view_reply_notification()
            output['new_reply_notifications'].append({'id':notification.id,'longitude':notification.totem.longitude,'latitude':notification.totem.latitude})
            output['show_notification_alert'] = True
        
        output['success'] = True

        print output
        RequestLog.add_request_log(client,longitude,latitude)
        client.save()

        return HttpResponse(simplejson.dumps(output), 'application/json')
    else:
        raise Http404

# ===========================================
# ----- FETCH_MESSAGES -----
# ===========================================

@csrf_exempt
def toggle_flag(request):

    if request.method == "POST":

        output = {}

        required_params = [
            'device_id',
            'message_id',
            'timestamp',
            'secret',
        ]

        # all parameters must be sent
        for param in required_params:
            if param not in request.POST.keys():
                output['success'] = False
                output['alert'] = "missing parameters"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # device id must be non-empty
        if request.POST['device_id'] == "":
                output['success'] = False
                output['alert'] = "empty device id"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # authorize secret
        if _auth_secret([
                            request.POST['device_id'],
                            request.POST['message_id'],
                            request.POST['timestamp']], request.POST['secret']) == False:

                output['success'] = False
                output['alert'] = "malformed request"
                return HttpResponse(simplejson.dumps(output), 'application/json')

        # client must exist in system and be registered
        try:
            client = Client.objects.get(device_id=request.POST['device_id'])
        except:
            output['success'] = False
            output['alert'] = "unknown client"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        # message must exist in system and be registered
        try:
            message = TotemMessage.objects.get(id=request.POST['message_id'])
        except:
            output['success'] = False
            output['alert'] = "unknown message"
            return HttpResponse(simplejson.dumps(output), 'application/json')

        output['state'] = Mark.create_or_toggle_mark(client,message,Mark.MARK_TYPES['flag'])
        output['success'] = True

        client.save()

        print output
        return HttpResponse(simplejson.dumps(output), 'application/json')
    else:
        raise Http404

# ===========================================
# ----- SECURITY -----
# ===========================================

def _auth_secret(params,hash_result):
    string = ""
    for param in params:
        string += str(param)
    string += settings.TOTEMS_SECRET
    print hash_result
    return hash_result == hash_function(string)

def hash_function(string):
    print hashlib.sha256(string).hexdigest()
    return hashlib.sha256(string).hexdigest()

def encrypt(msg):
    key = settings.TOTEMS_ENCRYPTION_KEY
    encryped = []
    for i, c in enumerate(msg):
        key_c = ord(key[i % len(key)])
        msg_c = ord(c)
        encryped.append(chr((msg_c + key_c) % 127))
    return ''.join(encryped)

def decrypt(encryped):
    key = settings.TOTEMS_ENCRYPTION_KEY
    msg = []
    for i, c in enumerate(encryped):
        key_c = ord(key[i % len(key)])
        enc_c = ord(c)
        msg.append(chr((enc_c - key_c) % 127))
    return ''.join(msg)
