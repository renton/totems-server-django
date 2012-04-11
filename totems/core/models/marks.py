from django.db import models
from clients import Client
from totems import TotemMessage
from django_extensions.db.fields import UUIDField
import datetime
from django.utils.timezone import utc

class Mark(models.Model):

    MARK_TYPE_SPAM = 0
    MARK_TYPE_REPORT = 1
    MARK_TYPE_UPVOTE = 2
    MARK_TYPE_DOWNVOTE = 3

    id = UUIDField(primary_key=True)
    created = models.DateTimeField(editable=False)
    client = models.ForeignKey(Client)
    totem_message = models.ForeignKey(TotemMessage)
    state = models.BooleanField(default=True)
    mark_type = models.IntegerField(null=False)
    last_activity = models.DateTimeField()

    class Meta:
        app_label = 'core'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.last_activity = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(Mark, self).save(*args, **kwargs)

    def toggle(self):
        self.state = not self.state
        self.save()

    @staticmethod
    def create_or_toggle_mark(client,message,mark_type):
        mark,created = Mark.objects.get_or_create(client=client,totem_message=message,mark_type=mark_type)
        if created:
            mark.save()
        else:
            mark.toggle()
        return mark

    @staticmethod
    def get_mark_count_for_message(message,mark_type):
        return Mark.objects.filter(totem_message=message,mark_type=mark_type,state=True).count()

    @staticmethod
    def get_marks_against(client,mark_type):
        #mark_type can be a list
        pass

    @staticmethod
    def is_marked_for_client(client,message,mark_type):
        try:
            mark = Mark.objects.get(totem_message=message,client=client,mark_type=mark_type,state=True)
        except Mark.DoesNotExist:
            return False
        return True
