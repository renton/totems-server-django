from django.db import models
import datetime

class WorldLayer(models.Model):
    name = models.CharField(max_length=30)
    created = models.DateTimeField(editable=False)

    class Meta:
        app_label = 'totems'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.today()
        super(WorldLayer, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.id
