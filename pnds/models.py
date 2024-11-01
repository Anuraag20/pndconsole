from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from market.models import (
    Exchange,
    Coin,
)
from django.db.models.signals import post_save
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

    message = models.ForeignKey('forums.Message', on_delete = models.CASCADE)

    pair = models.ForeignKey(Coin, on_delete = models.CASCADE, null = True, blank = True, related_name = 'pump_pair')
    target = models.ForeignKey(Coin, on_delete = models.CASCADE, null = True, blank = True, related_name = 'pump_target')
    
    exchanges = models.ManyToManyField(Exchange, related_name = 'schduled')
    scheduled_at = models.DateTimeField()
    
    notes = models.TextField(null = True, blank = True)

    false_alarm = models.BooleanField(default = False)
    pair_guessed = models.BooleanField(default = False)
    manually_corrected = models.BooleanField(default = False)

    def save(self, *args, **kwargs):
        
        if self.false_alarm:
            self.manually_corrected = True

        return super(ScheduledPump, self).save(*args, **kwargs)



@receiver(post_save, sender = ScheduledPump, dispatch_uid = "schedule_monitoring")
def schedule_monitoring(sender, instance: ScheduledPump, created, **kwargs):
    if instance.target and instance.exchanges.exists():
        print('Yaah')
        topic = f'pnd_{instance.id}'
        for exchange in instance.exchanges.all():  
            start_monitoring(
                    at = instance.scheduled_at,
                    exchange = exchange.name, 
                    target = instance.target.id, 
                    pair = instance.pair.id,
                    topic = topic
                )
        
        start_consuming(instance.scheduled_at, topic)
    else:
        print({f'message__{instance.message.forum_cls_name}': instance.message.forum})
        monitor_forum(
                    at = instance.scheduled_at - settings.FINE_GRAINED_MONITORING_BEFORE ,
                    forum = instance.message.forum,
                    pump = instance.id 
            )
