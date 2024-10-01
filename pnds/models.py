from django.db import models
from telegram.models import Message
from market.models import (
    Exchange,
    Coin,
    OHLCVData
)

# Create your models here.

class ScheduledPump(models.Model):

    message = models.ForeignKey(Message)



