from django.db import models

# Create your models here.


class Exchange(models.Model):

    display_name = models.CharField(max_length = 30, null = True, blank = True)
    name = models.CharField(max_length = 30)
    url = models.URLField(null = True, blank = True)
    logo = models.ImageField(null = True, blank = True)
    
    def __str__(self):
        return f'{self.display_name}({self.name})'


class Coin(models.Model):

    name = models.CharField(max_length = 30, null = True, blank = True)
    symbol = models.CharField(max_length = 10)

    def __str__(self):

        return f'{self.name}({self.symbol})'

class OHLVCQueryset(models.QuerySet):
   
    # edit this to make it functional later
    def annotate_load_delay(self):
        return self


class OHLCVDataManager(models.Manager):

    
    def get_queryset(self):
        return OHLVCQueryset(self.model, using = self._db)

    def annotate_load_delay(self):
        return self.get_queryset().annotate_load_delay()


class OHLCVData(models.Model):

    objects = OHLCVDataManager()
    # Create model manager to add db field to check for discrepancy (added_at - market_time)

    exchange = models.ForeignKey(Exchange, on_delete = models.CASCADE, related_name = 'datum')    
    coin = models.ForeignKey(Coin, on_delete = models.CASCADE, related_name = 'market_main')
    pair = models.ForeignKey(Coin, on_delete = models.CASCADE, related_name = 'market_pair')


    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    
    market_time = models.DateTimeField()
    added_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        
        verbose_name = 'OHLCV Data'
        verbose_name_plural = 'OHLCV Datum'


    










