from django.db import models
from django_extensions.db.fields import UUIDField
import datetime
from django.utils.timezone import utc

class Client(models.Model):
    id = UUIDField(primary_key=True)
    created = models.DateTimeField(editable=False)
    last_activity = models.DateTimeField()
    device_id = models.TextField(blank=True)
    meta_data = models.TextField(blank=True)
    is_banned = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    class Meta:
        app_label = 'core'
        verbose_name = 'client'
        verbose_name_plural = 'clients'

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = datetime.datetime.utcnow().replace(tzinfo=utc)
            self.last_activity = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(Client, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.id

    def deactivate(self):
        self.active = False
        self.save()

    def ban(self):
        self.is_banned = True
        self.save()

    def unban(self):
        self.is_banned = False
        self.save()

    def update_last_activity(self):
        self.last_activity = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.save()

    def get_notifications(self):
        pass

    def get_num_totems(self):
        pass

    def get_num_messages(self):
        pass

    def get_latest_messages(self):
        pass

    @staticmethod
    def get_or_register_client():
        pass

    @staticmethod
    def __register_client():
        pass
