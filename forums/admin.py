from django.contrib import admin
from .models import (
    TelegramChannel, 
    Message
)

@admin.register(TelegramChannel)
class TelegramChannelAdmin(admin.ModelAdmin):
    pass

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass

