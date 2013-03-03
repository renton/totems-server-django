from clients import Client
import datetime
from django.utils.timezone import utc

class BaseLog(models.Model):

    id = UUIDField(primary_key=True)
    created = models.DateTimeField(editable=False)

    class Meta:
        abstract = True
        app_label = 'core'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(BaseLog, self).save(*args, **kwargs)

class RequestLog(BaseLog):

    client = models.ForeignKey(Client)
    point = models.PointField(srid=4326)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.id
