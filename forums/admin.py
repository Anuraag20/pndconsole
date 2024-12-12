from django.contrib import admin
from .models import (
    TelegramChannel, 
    Message
)

@admin.register(TelegramChannel)
class TelegramChannelAdmin(admin.ModelAdmin):
    list_display = ('name', )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('forum_type', 'forum_name', 'content', 'sent_at', )
    list_display_links = ('forum_name', )

    def forum_type(self, instance):
        return instance.content_type.name.title()

    def forum_name(self, instance):
        return instance.forum.name

    

