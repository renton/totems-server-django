from django.db import models
from django_extensions.db.fields import UUIDField
import datetime

class Client(models.Model):
    id = UUIDField(primary_key=True)
    created = models.DateTimeField(editable=False)
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
            self.created = datetime.datetime.today()
        super(Client, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.id

    def deactivate(self):
        self.active = False

    def ban(self):
        self.is_banned = True

    def unban(self):
        self.is_banned = False

    def get_notifications(self):
        pass

    def get_num_totems(self):
        pass

    def get_num_messages(self):
        pass

    def get_latest_messages(self):
        pass

    @staticmethod
    def register_client():
        pass
