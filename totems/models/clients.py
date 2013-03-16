from django.db import models
import datetime
from django.utils.timezone import utc
from random import randrange
import os

class Client(models.Model):
    created = models.DateTimeField(editable=False)
    last_activity = models.DateTimeField()

    device_id = models.TextField(null=False,unique=True)
    device_name = models.TextField(null=False)
    device_version = models.TextField(null=False)
    device_platform = models.TextField(null=False)

    is_banned = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    is_bot = models.BooleanField(default=False)

    registration_longitude = models.FloatField()
    registration_latitude = models.FloatField()

    class Meta:
        app_label = 'totems'
        verbose_name = 'client'
        verbose_name_plural = 'clients'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.last_activity = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(Client, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.id)

    def deactivate(self):
        self.active = False
        self.save()

    def ban(self):
        self.is_banned = True
        self.save()

    def unban(self):
        self.is_banned = False
        self.save()

    def remove_all_activity(self):
        #remove all totems,messages,marks
        pass

    @staticmethod
    def remove_bot_activity():
        #remove all bots and their activity
        pass

    @staticmethod
    def gen_bots(amount):
        for i in range(amount):
            r_long = randrange(-180,180)
            r_lat = randrange(-90,90)
            r_id = os.urandom(16).encode('hex')
            Client.get_or_register_client(r_id,"fake device","fake platform","1.0",r_long,r_lat,True)

    @staticmethod
    def get_or_register_client(device_id,device_name="unknown",device_platform="unknown",device_version="unknown",longitude=None,latitude=None,is_bot=False):
        client, created = Client.objects.get_or_create(device_id=device_id,defaults={'device_name':device_name,'device_platform':device_platform,'device_version':device_version,'is_bot':is_bot,'registration_longitude':longitude,'registration_latitude':latitude})
        if created:
            client.save()
        return client, created
