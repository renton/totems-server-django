from django.contrib import admin

from totems.core.models import Client, WorldLayer, Zone, MarkReport, MarkSpam, MarkVote, RequestLog, FlagNotification, ReplyNotification, EmptyRequestNotification, Totem, TotemMessage

admin.site.register(Client)
admin.site.register(WorldLayer)
admin.site.register(Zone)
admin.site.register(Totem)
admin.site.register(TotemMessage)
admin.site.register(MarkReport)
admin.site.register(MarkSpam)
admin.site.register(MarkVote)
admin.site.register(RequestLog)
admin.site.register(FlagNotification)
admin.site.register(ReplyNotification)
admin.site.register(EmptyRequestNotification)
