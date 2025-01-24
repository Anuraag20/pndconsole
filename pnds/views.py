from django.db.models import (
    Avg,
    Count,
    F,
    Q, 
)
from django.db.models.functions import Extract
from django.conf import settings
from django.shortcuts import render
from numpy import who
from forums.models import Message
from market.models import OHLCVData
from .models import ScheduledPump
from django.contrib.auth.decorators import login_required

# Create your views here.

#@login_required
def index(request):
   
    pumps = ScheduledPump.objects.filter(false_alarm = False)
    candles = OHLCVData.objects.annotate_load_delay()    
    

    manually_classified = candles.filter(is_pump_non_ml__isnull = False).count() or 1

    stats = {
        'pumps_count': pumps.count(),
        'exchanges_count': candles.values('exchange').distinct().count(),
        'coins_count': candles.values('coin').distinct().count(),
        #'avg_load_delay': str(round(avg_load_delay.total_seconds()) if avg_load_delay else '-') + ' seconds',
        'pumps_by_week': list(pumps.annotate(weekday = Extract('scheduled_at', 'DOW')).values('weekday').annotate(c = Count('weekday'))),
        'msg_count': Message.objects.all().count(),
        'pumps_by_channel': list(pumps.annotate(channel =  F('message__telegramchannel__name')).values('channel').annotate(c = Count('channel'))),
        'accuracy': str(round(
            (
                (candles.filter(is_pump = True, is_pump_non_ml = True).count() + candles.filter(is_pump = False, is_pump_non_ml = False).count())
                / manually_classified) * 100, 2
            )) + '%'
        
        }

    context = {
            'pumps': pumps,
            'stats': stats
        }
    return render(request, 'pnds/index.html', context)

#@login_required
def pump_view(request, pump_id):
    
    pump = ScheduledPump.objects.get(id = pump_id)
    exchanges = pump.exchanges.values_list('name', flat = True).distinct()

    context = {
        'pump': pump,
        'exchanges': exchanges
    }

    if not pump.is_active:
        
        exchange_data = {}

        data = OHLCVData.objects.filter(
                Q(market_time__gt = pump.scheduled_at - settings.FETCH_PREVIOUS_DEFAULT)
                &
                Q(market_time__lte = pump.scheduled_at + settings.STOP_CONSUMING_AFTER)
                &
                Q(exchange__name__in = exchanges)
                &
                Q(coin = pump.target)
                &
                Q(pair = pump.pair)
            )
        for exchange in exchanges:
            exchange_data[exchange] = list(data.filter(exchange__name = exchange).get_candles())

        context['exchange_data'] = exchange_data

    return render(request, 'pnds/pump.html', context)
