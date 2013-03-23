from django.db import models
from worldlayers import WorldLayer
from clients import Client
import datetime, time
from django.utils.timezone import utc
from ..tools import pretty_date

class Totem(models.Model):
    created = models.DateTimeField(editable=False)
    last_activity = models.DateTimeField()
    worldlayer = models.ForeignKey(WorldLayer)

    rating = models.IntegerField(default=50)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(Client)

    longitude = models.FloatField()
    latitude = models.FloatField()

    class Meta:
        app_label = 'totems'
        verbose_name = 'totem'
        verbose_name_plural = 'totems'
        
    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.last_activity = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(Totem, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.id)

    def get_message_count(self):
        return TotemMessage.objects.filter(totem=self).count()

    def get_parent_message(self):
        parent = TotemMessage.objects.get(totem=self,parent_message=None)
        parent.x_num_replies = parent.get_num_replies()
        return parent

    def build_totem_message_tree(self,check_owner_device_id=None,depth=None):
        parent_message = self.get_parent_message()
        return parent_message.build_message_tree_from_node(check_owner_device_id,depth)

    def build_tree_display_repr(self):
        parent_message = self.get_parent_message()
        return parent_message.list_from_node()

    def remove(self):
        messages = TotemMessage.objects.filter(totem=self)
        for message in messages:
            message.remove()
        self.active = False
        self.save()

    @staticmethod
    def get_totem_count_by_client(client):
        return Totem.objects.filter(owner=client).count()

    @staticmethod
    def get_totems_by_client(client):
        return Totem.objects.filter(owner=client)

    @staticmethod
    def add_totem(client,longitude,latitude,message,worldlayer):
        #create totem
        new_totem = Totem()
        new_totem.worldlayer = worldlayer
        new_totem.owner = client
        new_totem.longitude = longitude
        new_totem.latitude = latitude
        new_totem.save()

        #create parent message
        new_message = TotemMessage()
        new_message.message = message
        new_message.totem = new_totem
        new_message.owner = client
        new_message.parent_message = None
        new_message.save()

        client.save()

        return new_totem

class TotemMessage(models.Model):
    created = models.DateTimeField(editable=False)
    active = models.BooleanField(default=True)
    message = models.TextField()
    rating = models.IntegerField(default=50)
    totem = models.ForeignKey(Totem)
    parent_message = models.ForeignKey('self', null=True, blank=True)
    owner = models.ForeignKey(Client)
    reply_notification = models.BooleanField(default=False)
    reply_notification_read = models.BooleanField(default=False)

    class Meta:
        app_label = 'totems'
        verbose_name = 'message'
        verbose_name_plural = 'messages'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.utcnow().replace(tzinfo=utc)
        #update last modified of parent totem
        if self.totem:
            self.totem.save()
        super(TotemMessage, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.id)

    def get_direct_children(self):

        children = TotemMessage.objects.filter(totem=self.totem,parent_message=self).order_by('-created')

        for child in children:
            child.x_num_replies = child.get_num_replies()

        return children

    def get_num_replies(self):
        return TotemMessage.objects.filter(totem=self.totem,parent_message=self).count()

    def reply_message(self, message, client):
        reply = TotemMessage()
        reply.message = message
        reply.parent_message = self
        reply.owner = client
        reply.totem = self.totem
        reply.save()

        if self.owner != client:
            self._set_reply_notification()

        self.owner.save()

    def _set_reply_notification(self):
        self.reply_notification = True
        self.reply_notification_read = False
        self.save()

    def view_reply_notification(self):
        self.reply_notification = True
        self.reply_notification_read = True
        self.save()

    def view_reply_notification_replies(self):
        self.reply_notification = False
        self.reply_notification_read = False
        self.save()

    def build_message_tree_from_node(self,check_owner_device_id=None,depth=None):
        #TODO - expensive. too many db calls
        node = {}

        timestamp = time.mktime(self.created.timetuple())

        node['id'] = self.id

        if self.active == True:
            node['message'] = self.message
        else:
            node['message'] = ""

        node['created'] = str(self.created)
        node['created_pretty'] = pretty_date(int(timestamp))
        node['is_owner'] = self.totem.owner.device_id == check_owner_device_id
        node['active'] = self.active
        node['is_totem_head'] = self.is_totem_head()

        if depth == 0:
            node['num_replies'] = self.get_num_replies()
        else:
            node['children'] = []
            children = self.get_direct_children()
            node['num_replies'] = len(children)

            if depth != None:
                depth -= 1

            for child in children:
                node['children'].append(child.build_message_tree_from_node(check_owner_device_id,depth))

        return node

    def print_from_node(self,depth=0):
        #TODO - expensive. too many db calls
        print str(depth)+" "+self.message
        children = self.get_direct_children()
        for child in children:
            child.print_from_node(depth+1)

    def list_from_node(self,depth=0):
        #TODO - expensive. too many db calls
        output = []
        output.append([depth,self])
        children = self.get_direct_children()
        for child in children:
            output = output + child.list_from_node(depth+50)
        return output

    def remove(self):
        self.active = False
        self.save()

    def is_totem_head(self):
        return self.parent_message == None

    @property
    def get_flag_count(self):
        from marks import Mark
        return Mark.objects.filter(totem_message=self,mark_type=Mark.MARK_TYPES['flag']).count()

    @staticmethod
    def get_all_reply_notifications_for_client(client):
        return TotemMessage.objects.filter(owner=client,reply_notification=True)

    @staticmethod
    def get_all_unread_reply_notifications_for_client(client):
        return TotemMessage.objects.filter(owner=client,reply_notification=True,reply_notification_read=False)

    @staticmethod
    def get_message_count_by_client(client):
        return TotemMessage.objects.filter(owner=client).count()

    @staticmethod
    def get_messages_by_client(client):
        return TotemMessage.objects.filter(owner=client)
