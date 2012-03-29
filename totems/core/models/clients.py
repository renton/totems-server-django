from django.db import models
from django_extensions.db.fields import UUIDField
import datetime

class Client(models.Model):
    id = UUIDField(primary_key=True)
    created = models.DateTimeField(editable=False)

    class Meta:
        app_label = 'totems_core'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.today()
        super(Client, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.id
