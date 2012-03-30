from django.db import models
from django_extensions.db.fields import UUIDField
import datetime

class BaseNotification(models.Model):

    id = UUIDField(primary_key=True)
    created = models.DateTimeField(editable=False)

    class Meta:
        abstract = True
        app_label = 'core'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.today()
        super(BaseNotification, self).save(*args, **kwargs)

class FlagNotification(BaseNotification):

    def __unicode__(self):
        return self.id

class ReplyNotification(BaseNotification):

    def __unicode__(self):
        return self.id

class EmptyRequestNotification(BaseNotification):

    def __unicode__(self):
        return self.id
