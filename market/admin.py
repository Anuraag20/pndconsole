from django.contrib import admin
from .models import (
    
    Exchange,
    Coin,
    OHLCVData

)

from django.contrib.admin import DateFieldListFilter
# Register your models here.


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
   list_display = ('display_name', 'name', ) 

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ('id', 'symbol', )

@admin.register(OHLCVData)
class OHLCVDataAdmin(admin.ModelAdmin):

    list_filter = (
        ('market_time', DateFieldListFilter),
        ('is_pump')
    )
    list_display = ('exchange_name', 'coin', 'pair', 'market_time', 'open', 'high', 'low', 'close', 'volume', 'is_pump', 'is_pump_non_ml')
    list_display_links = ('coin', )
    list_editable = ('is_pump_non_ml', )

    def exchange_name(self, instance):
        return instance.exchange.display_name 
