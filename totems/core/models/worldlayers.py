from django.db import models
from django_extensions.db.fields import UUIDField
import datetime

class WorldLayer(models.Model):
    id = UUIDField(primary_key=True)
    name = models.CharField(max_length=30)
    created = models.DateTimeField(editable=False)

    class Meta:
        app_label = 'core'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.today()
        super(WorldLayer, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.id
