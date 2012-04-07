from django.contrib.gis.db import models
from django_extensions.db.fields import UUIDField
from worldlayers import WorldLayer
from clients import Client
import datetime
from django.utils.timezone import utc

class Totem(models.Model):
    id = UUIDField(primary_key=True)
    created = models.DateTimeField(editable=False)
    last_activity = models.DateTimeField()
    worldlayer = models.ForeignKey(WorldLayer)

    rating = models.IntegerField(default=50)

    active = models.BooleanField(default=True)
    is_spam = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)

    owner = models.ForeignKey(Client)

    #point = models.PointField(srid=4326)
    #objects = models.GeoManager()

    class Meta:
        app_label = 'core'
        verbose_name = 'totem'
        verbose_name_plural = 'totems'
        

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.utcnow().replace(tzinfo=utc)
            self.last_activity = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(Totem, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.id

    def update_last_activity(self):
        self.last_activity = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()

    def get_message_count(self):
        return TotemMessage.objects.filter(totem=self).count()

    def get_parent_message(self):
        parent = TotemMessage.objects.get(totem=self,parent_message=None)
        parent.x_num_replies = parent.get_num_replies()
        return parent

    def build_totem_message_tree(self):
        parent_message = self.get_parent_message()
        return parent_message.build_message_tree_from_node()

    def build_tree_display_repr(self):
        parent_message = self.get_parent_message()
        return parent_message.list_from_node()

    def set_flagged(self):
        self.is_flagged = True
        self.save()

    def set_spam(self):
        self.is_spam = True
        self.save()

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
    def add_totem(client,point,message,worldlayer):
        #create totem
        new_totem = Totem()
        new_totem.worldlayer = worldlayer
        new_totem.owner = client
        new_totem.save()

        #create parent message
        new_message = TotemMessage()
        new_message.message = message
        new_message.totem = new_totem
        new_message.owner = client
        new_message.parent_message = None
        new_message.save()

        client.update_last_activity()

class TotemMessage(models.Model):
    id = UUIDField(primary_key=True)
    created = models.DateTimeField(editable=False)

    active = models.BooleanField(default=True)
    is_spam = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)

    message = models.TextField()

    rating = models.IntegerField(default=50)

    totem = models.ForeignKey(Totem)
    parent_message = models.ForeignKey('self', null=True, blank=True)
    owner = models.ForeignKey(Client)

    class Meta:
        app_label = 'core'
        verbose_name = 'message'
        verbose_name_plural = 'messages'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.utcnow().replace(tzinfo=utc)
        #update last modified of parent totem
        if self.totem:
            self.totem.update_last_activity()
        super(TotemMessage, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.id

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

        self.owner.update_last_activity()

    def build_message_tree_from_node(self):
        #TODO - expensive. too many db calls
        node = {}
        node['message'] = self
        node['children'] = []

        children = self.get_direct_children()
        for child in children:
            node['children'].append(child.build_message_tree_from_node())
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

    def mark_spam(self,client):
        # get_or_create markspam model
        pass

    def mark_flag(self,client):
        # get_or_create create markflag model
        pass

    def mark_upvote(self,client):
        # get_or_create vote model - switch to up
        pass

    def mark_downvote(self,client):
        # get_or
        pass

    def remove(self):
        self.active = False
        self.save()

    def set_spam(self):
        self.is_spam = True
        self.save()

    def set_flagged(self):
        self.is_flagged = True
        self.save()

    @staticmethod
    def get_message_count_by_client(client):
        return TotemMessage.objects.filter(owner=client).count()

    @staticmethod
    def get_messages_by_client(client):
        return TotemMessage.objects.filter(owner=client)
