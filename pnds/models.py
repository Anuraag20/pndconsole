from django.db import models
from market.models import (
    Exchange,
    Coin,
    OHLCVData
)

# Create your models here.

class ScheduledPump(models.Model):

    message = models.ForeignKey('forums.Message', on_delete = models.CASCADE)

    pair = models.ForeignKey(Coin, on_delete = models.CASCADE, null = True, blank = True, related_name = 'pump_pair')
    target = models.ForeignKey(Coin, on_delete = models.CASCADE, null = True, blank = True, related_name = 'pump_target')
    
    exchanges = models.ManyToManyField(Exchange, related_name = 'schduled')
    scheduled_at = models.DateTimeField(null = True, blank = True)
    
    notes = models.TextField(null = True, blank = True)

    false_alarm = models.BooleanField(default = False)
    pair_guessed = models.BooleanField(default = False)
    manually_corrected = models.BooleanField(default = False)

    def save(self, *args, **kwargs):
        
        if self.false_alarm:
            self.manually_corrected = True

        return super(ScheduledPump, self).save(*args, **kwargs)
