from django.contrib import admin
from .models import (
    
    Exchange,
    Coin,
    OHLCVData

)

# Register your models here.


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    pass

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    pass

@admin.register(OHLCVData)
class OHLCVDataAdmin(admin.ModelAdmin):
    pass
