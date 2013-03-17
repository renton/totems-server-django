from clients import Client
from django.db import models
import datetime
from django.utils.timezone import utc

class BaseLog(models.Model):

    created = models.DateTimeField(editable=False)

    class Meta:
        abstract = True
        app_label = 'totems'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(BaseLog, self).save(*args, **kwargs)

class RequestLog(BaseLog):

    client = models.ForeignKey(Client)
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __unicode__(self):
        return str(self.client.device_id)+" at "+str(self.created)

    @staticmethod
    def add_request_log(client,longitude,latitude):
        new_log = RequestLog()
        new_log.client = client
        new_log.longitude = longitude
        new_log.latitude = latitude
        new_log.save()
