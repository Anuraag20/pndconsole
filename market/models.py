from typing import Union
import ccxt.pro as ccxt
from django.conf import settings
from django.db import models
from django.db.models.functions import Extract, TruncSecond

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
For accessing any of the ccxt methods, the object needs to be put in a context manager
'''
class Exchange(models.Model):

    display_name = models.CharField(max_length = 30, null = True, blank = True)
    name = models.CharField(max_length = 30)
    url = models.URLField(null = True, blank = True)
    logo = models.ImageField(null = True, blank = True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # This is only initialized when used with a context manager
        self.__pvt_ccxt = getattr(ccxt, self.name, None)

    def __str__(self):
        return f'{self.display_name}({self.name})'
    
    def __enter__(self):
        self.__pvt_ccxt = self.__pvt_ccxt()
    
    def __exit__(self, *args, **kwargs):
        async_to_sync(self.ccxt_exc.close)()
        self.__pvt_ccxt = self.ccxt_exc.__class__
        print('still exited!')


    async def __aenter__(self):
        self.__enter__()

    async def __aexit__(self, *args, **kwargs):
        await self.ccxt_exc.close()
        self.__pvt_ccxt = self.ccxt_exc.__class__
        print('Got it baby!')


    @property
    def ccxt_exc(self):
        assert self.__pvt_ccxt, f'{self.display_name}({self.name}) is not supported by CCXT.'
        return self.__pvt_ccxt

    def fetch_ohlcv(self, target: Coin, pair: Coin, timeframe = '1m', since = None):
        if not since: 
            since = round( (timezone.now() - settings.FETCH_PREVIOUS_DEFAULT).timestamp() * 1000 ) 

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



class OHLCVQueryset(models.QuerySet):
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend = settings.DATABASES[self.db]['ENGINE']


    # edit this to make it functional later
    def annotate_load_delay(self):
        return self
    
    def annotate_timestamp(self):
     
        
        if 'sqlite' in self.backend:

            return self.annotate(timestamp = models.ExpressionWrapper(
                    models.Func(
                        models.Value('%s'),
                        models.F('market_time'),
                        function = 'STRFTIME',
                    ) * 1000, 
                    output_field = models.IntegerField() 
                )
                )

        elif 'postgres' in self.backend:
            return self.annotate(timestamp = Extract('market_time', 'epoch'))

        return self

    def get_candles(self):
        return self.annotate_timestamp().values_list('open', 'high', 'low', 'close', 'volume', 'timestamp', 'exchange__name', 'coin__symbol', 
                                                          'pair__symbol')



class OHLCVData(models.Model):

    objects = OHLCVQueryset.as_manager()

    exchange = models.ForeignKey(Exchange, on_delete = models.CASCADE, related_name = 'datum')    
    coin = models.ForeignKey(Coin, on_delete = models.CASCADE, related_name = 'market_main')
    pair = models.ForeignKey(Coin, on_delete = models.CASCADE, related_name = 'market_pair')

    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    
    market_time = models.DateTimeField()
    received_at = models.DateTimeField() # Specifies when the object was received by the producer
    added_at = models.DateTimeField(auto_now_add = True)
    
    is_pump = models.BooleanField(
                default = False,
                help_text = 'This boolean value is set by the classifier '
            ) 
    is_pump_non_ml = models.BooleanField(
                        default = False,
                        help_text = 'This boolean value will either be set manually or programatically'
                    )

    
    @classmethod
    def from_stream(cls, data, received_at, is_pump = False, is_pump_non_ml = False):

        assert settings.STREAMING_VERSION == data[0], f'Incorrect version for this consumer node. Please switch to version {settings.STREAMING_VERSION}'
        
        return cls.from_candle(*data[1:4], received_at, data[4:10], is_pump, is_pump_non_ml)



    @classmethod
    def from_candle(cls, 
                    exchange_id: int, coin_id: int, pair_id: int, received_at: int,
                    candle: list, is_pump: bool = False, is_pump_non_ml: bool = False
                    ):
        return cls.objects.get_or_create(
                    exchange_id = exchange_id,
                    coin_id = coin_id,
                    pair_id = pair_id,
                    market_time =  timezone.make_aware( timezone.datetime.fromtimestamp(candle[0]/1000) ),
                    defaults = {
                        'received_at': timezone.make_aware( timezone.datetime.fromtimestamp(received_at/1000) ),
                        'open': candle[1],
                        'high': candle[2],
                        'low': candle[3],
                        'close': candle[4],
                        'volume': candle[5],
                        'is_pump': is_pump,
                        'is_pump_non_ml': is_pump_non_ml
                    }
                )[0]


    def get_candle(self):
        return [self.open, self.high, self.low, self.close, self.volume, self.market_time.timestamp()*1000, self.exchange.name, self.coin.symbol, self.pair.symbol]

    class Meta:
        
        verbose_name = 'OHLCV Data'
        verbose_name_plural = 'OHLCV Datum'


   










