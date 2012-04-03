from django.contrib.gis.db import models
from django_extensions.db.fields import UUIDField
from worldlayers import WorldLayer
from clients import Client
import datetime

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
            self.created = datetime.datetime.today()
        super(Totem, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.id

    def update_last_activity(self):
        self.last_activity = datetime.now()
        self.save()

class TotemMessage(models.Model):
    id = UUIDField(primary_key=True)
    created = models.DateTimeField(editable=False)

    active = models.BooleanField(default=True)
    is_spam = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)

    message = models.TextField()

    rating = models.IntegerField(default=50)

    totem = models.ForeignKey(Totem)
    parent_message = models.ForeignKey('self', null=True)
    owner = models.ForeignKey(Client)

    class Meta:
        app_label = 'core'
        verbose_name = 'message'
        verbose_name_plural = 'messages'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.today()
        super(TotemMessage, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.id
