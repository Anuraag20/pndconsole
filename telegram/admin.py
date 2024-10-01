from django.contrib import admin

from .models import (
       Channel,
       Message
)

# Register your models here.

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    pass


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass


