from django.contrib import admin

from totems.core.models import Client, WorldLayer, Totem, TotemMessage, RequestLog, Mark

admin.site.register(Client)
admin.site.register(WorldLayer)
#admin.site.register(Zone)
admin.site.register(Totem)
admin.site.register(TotemMessage)
admin.site.register(Mark)
#admin.site.register(MarkSpam)
#admin.site.register(MarkVote)
admin.site.register(RequestLog)
#admin.site.register(FlagNotification)
#admin.site.register(ReplyNotification)
#admin.site.register(EmptyRequestNotification)
