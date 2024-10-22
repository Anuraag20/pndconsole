import ccxt.pro as ccxt
from django.db import models
from django.utils import timezone
from datetime import timedelta
from asgiref.sync import async_to_sync

# Create your models here.

class Coin(models.Model):

    name = models.CharField(max_length = 30, null = True, blank = True)
    symbol = models.CharField(max_length = 10)

    def __str__(self):
        return f'{self.name}({self.symbol})'

'''
For accessing any of the ccxt methods, 

'''
class Exchange(models.Model):

    display_name = models.CharField(max_length = 30, null = True, blank = True)
    name = models.CharField(max_length = 30)
    url = models.URLField(null = True, blank = True)
    logo = models.ImageField(null = True, blank = True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # This is only initialized when used with a context manager
        self._ccxt_exc = getattr(ccxt, self.name, None)

    @property
    def ccxt_exc(self) -> ccxt.Exchange:
        assert self._ccxt_exc, f'{self.display_name}({self.name}) is not supported by CCXT.'
        return self._ccxt_exc

    @ccxt_exc.setter
    def ccxt_exc(self, value):
        assert self._ccxt_exc, f'{self.display_name}({self.name}) is not supported by CCXT.'
        self._ccxt_exc = value


    def __str__(self):
        return f'{self.display_name}({self.name})'
    
    def __enter__(self):
        self.ccxt_exc = self._ccxt_exc()
    
    def __exit__(self, *args, **kwargs):
        async_to_sync(self.ccxt_exc.close)()
        self.ccxt_exc = self.ccxt_exc.__class__
        print('still exited!')


    async def __aenter__(self):
        self.__enter__()

    async def __aexit__(self, *args, **kwargs):
        await self.ccxt_exc.close()
        self.ccxt_exc = self.ccxt_exc.__class__
        print('Got it baby!')



    def fetch_ohlcv(self, target: Coin, pair: Coin, timeframe = '1m', since = None):
        if not since: 
            since = round( (timezone.now() - timedelta(hours = 1)).timestamp() * 1000 ) 

        return self.ccxt_exc.fetch_ohlcv(
                    f'{target.symbol}/{pair.symbol}',
                    timeframe = timeframe,
                    since = since
                )



    def watch_ohlcv(self, target: Coin, pair: Coin, timeframe = '1m'):
        return self.ccxt_exc.watch_ohlcv(
                    f'{target.symbol}/{pair.symbol}',
                    timeframe = timeframe
                )



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


    










