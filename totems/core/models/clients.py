from django.contrib.gis.db import models
from django.contrib.gis.geos import *
from django_extensions.db.fields import UUIDField
import datetime
from django.utils.timezone import utc
import random

class Client(models.Model):
    id = UUIDField(primary_key=True)
    created = models.DateTimeField(editable=False)
    last_activity = models.DateTimeField()
    device_id = models.TextField(null=False,unique=True)
    meta_data = models.TextField(blank=True)
    is_banned = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    is_bot = models.BooleanField(default=False)

    registration_point = models.PointField(srid=4326)
    objects = models.GeoManager()

    class Meta:
        app_label = 'core'
        verbose_name = 'client'
        verbose_name_plural = 'clients'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.last_activity = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(Client, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.id

    def deactivate(self):
        self.active = False
        self.save()

    def ban(self):
        self.is_banned = True
        self.save()

    def unban(self):
        self.is_banned = False
        self.save()

    def update_last_activity(self):
        self.last_activity = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()

    def remove_all_activity(self):
        #remove all totems,messages,marks
        pass

    @staticmethod
    def create_random_point():
        return Point(random.randrange(-180,180),random.randrange(-85,85))

    @staticmethod
    def remove_bot_activity():
        #remove all bots and their activity
        pass

    @staticmethod
    def get_or_register_client(device_id,is_bot=False):
        client, created = Client.objects.get_or_create(device_id=device_id, defaults={'is_bot':is_bot,'registration_point':Client.create_random_point()})
        if created:
            client.save()
        return client
