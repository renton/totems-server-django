from django.db import models
from clients import Client
from totems import TotemMessage
from django_extensions.db.fields import UUIDField
import datetime

class BaseMark(models.Model):

    id = UUIDField(primary_key=True)
    created = models.DateTimeField(editable=False)
    client = models.ForeignKey(Client)
    totem_message = models.ForeignKey(TotemMessage)

    class Meta:
        abstract = True
        app_label = 'core'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.today()
        super(BaseMark, self).save(*args, **kwargs)

class MarkReport(BaseMark):

    def __unicode__(self):
        return self.id

class MarkSpam(BaseMark):

    def __unicode__(self):
        return self.id

class MarkVote(BaseMark):

    def __unicode__(self):
        return self.id
