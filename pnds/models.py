from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from websockets.http11 import MAX_LINE_LENGTH
from market.models import (
    IntervalField,
    Exchange,
    Coin,
    OHLCVData
)
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from .utils import (
        start_monitoring,
        start_consuming,
        monitor_forum
)
# Create your models here.
 
class ScheduledPumpQueryset(models.QuerySet):
    
    def upcoming(self, **kwargs):
        return self.filter(
                    Q(scheduled_at__lte = timezone.now() + settings.FINE_GRAINED_MONITORING_BEFORE)
                    &
                    Q(scheduled_at__gt = timezone.now()),
                    **kwargs
                )



class ScheduledPump(models.Model):
    
    objects = ScheduledPumpQueryset.as_manager()

    message = models.OneToOneField('forums.Message', on_delete = models.CASCADE)

    pair = models.ForeignKey(Coin, on_delete = models.CASCADE, null = True, blank = True, related_name = 'pump_pair')
    target = models.ForeignKey(Coin, on_delete = models.CASCADE, null = True, blank = True, related_name = 'pump_target')
    
    exchanges = models.ManyToManyField(Exchange, related_name = 'schduled')
    interval = IntervalField()

    scheduled_at = models.DateTimeField(null = True, blank = True)
    
    notes = models.TextField(null = True, blank = True)

    false_alarm = models.BooleanField(default = False)
    pair_guessed = models.BooleanField(default = False)
    manually_corrected = models.BooleanField(default = False)
    
    @property
    def is_active(self):
        return (self.scheduled_at <= timezone.now()) and (self.scheduled_at + settings.STOP_CONSUMING_AFTER > timezone.now())

    @property
    def is_upcoming(self):
        return self.scheduled_at > timezone.now()
    
    @property
    def candles(self):
        return OHLCVData.objects.filter(
                market_time__gte = self.scheduled_at - settings.FETCH_PREVIOUS_DEFAULT,
                market_time__lte = self.scheduled_at + settings.STOP_PRODUCING_AFTER,
                coin = self.target,
                pair = self.pair
                )

    @property
    def exchanges_name(self):
        return ', '.join(self.exchanges.all().values_list('display_name', flat = True))

    def save(self, *args, **kwargs):
        
        if self.false_alarm:
            self.manually_corrected = True

        return super(ScheduledPump, self).save(*args, **kwargs)
    

    def __str__(self):

        string = f'Pump Scheduled at {self.scheduled_at} on {self.exchanges_name}'
        if self.target:
            string += f'({self.target.symbol}/{self.pair.symbol})'
        string += '.'
        return string
# We user m2m_changed instead of post_save to reliably get the exhanges on save.

@receiver(m2m_changed, sender = ScheduledPump.exchanges.through, dispatch_uid = "schedule_monitoring")
def schedule_message_monitoring(sender, instance: ScheduledPump, *args, **kwargs):
    
    if not instance.target:
        print(f'The messages from {instance.message.forum_cls_name}: {instance.message.forum} will be monitored.')
        monitor_forum(
                    at = instance.scheduled_at - settings.FINE_GRAINED_MONITORING_BEFORE ,
                    forum = instance.message.forum,
                    pump = instance.id 
            )

@receiver(post_save, sender = ScheduledPump, dispatch_uid = "schedule_coin_monitoring")
def schedule_monitoring(sender, instance: ScheduledPump, created, **kwargs):

    if instance.target and instance.exchanges.exists():
        topic = f'pnd_{instance.id}'
        for exchange in instance.exchanges.all():  
            start_monitoring(
                    at = instance.scheduled_at,
                    exchange = exchange.name, 
                    target = instance.target.id, 
                    pair = instance.pair.id,
                    topic = topic,
                    freq = instance.interval 
                )

        start_consuming(instance.scheduled_at, topic)
