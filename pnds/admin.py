from django.contrib import admin
from .models import ScheduledPump
# Register your models here.

@admin.register(ScheduledPump)
class ScheduledPumpAdmin(admin.ModelAdmin):
    list_display = ('target', 'pair', 'exchanges_name', 'scheduled_at', 'false_alarm',)
    list_editable = ('false_alarm', )

    def exchanges_name(self, instance):
        return instance.exchanges_name
    exchanges_name.short_description = 'exchanges'
