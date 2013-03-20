from django.db import models
from clients import Client
from totems import TotemMessage
import datetime
from django.utils.timezone import utc

class Mark(models.Model):

    MARK_TYPES = {
        "flag":0,
    }

    created = models.DateTimeField(editable=False)
    last_activity = models.DateTimeField()
    client = models.ForeignKey(Client)
    totem_message = models.ForeignKey(TotemMessage)
    mark_type = models.IntegerField(null=False)

    class Meta:
        app_label = 'totems'
        verbose_name = 'mark'
        verbose_name_plural = 'marks'
        unique_together = ("client", "totem_message")

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.last_activity = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(Mark, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.client.device_id)+" : "+str(self.totem_message.message)

    @staticmethod
    def create_or_toggle_mark(client,message,mark_type):
        mark,created = Mark.objects.get_or_create(client=client,totem_message=message,mark_type=mark_type)
        if created:
            mark.save()
            return True
        else:
            mark.delete()
            return False

    @staticmethod
    def get_mark_count_for_message(message,mark_type):
        return Mark.objects.filter(totem_message=message,mark_type=mark_type,state=True).count()

    @staticmethod
    def is_marked_for_client(client,message,mark_type):
        try:
            mark = Mark.objects.get(totem_message=message,client=client,mark_type=mark_type,state=True)
        except Mark.DoesNotExist:
            return False
        return True
