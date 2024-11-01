from django.contrib import admin
from .models import ScheduledPump

# Register your models here.

@admin.register(ScheduledPump)
class ScheduledPumpAdmin(admin.ModelAdmin):
    pass
