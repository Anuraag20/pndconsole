
from django_celery_beat.models import (
        PeriodicTask, 
        ClockedSchedule
)

import json
import pandas as pd
import numpy as np
from django.utils import timezone

from asgiref.sync import (
        async_to_sync
)
from market.models import OHLCVData

def _detector(model, x, y):

    input = pd.Series([y], index = [timezone.make_aware( timezone.datetime.fromtimestamp(x/1000) )])
    return bool(model.predict(input).iloc[0])

def get_detector(data, timestamp_idx = 0, target_idx = 4):
    data = np.array(data)
    from adtk.detector import InterQuartileRangeAD

    index = [timezone.make_aware( timezone.datetime.fromtimestamp(t/1000) ) for t in data[:, timestamp_idx].astype(int)]
    input = pd.Series(data[:, target_idx].astype(float), index = index)
    iqr = InterQuartileRangeAD(c = 1.5)
    iqr.fit(input)

    return lambda x, y: _detector(iqr, x, y)


def create_candle(candle, serializer, layer, detector = None):
        
        # 0 and 4 are the indices of the timestamp and the closing price respectively
        ohlcv = OHLCVData.from_stream(
                    data = serializer(candle),
                    received_at = round(timezone.now().timestamp() * 1000),
                    is_pump = False if not detector else detector(candle[0], candle[4]),
                    is_pump_non_ml = False
                ) 

        socket_message = ohlcv.get_candle()
        data = {
                    'type': 'market_data',
                    'message': [socket_message]
                }
        async_to_sync(layer.group_send)(f'{socket_message[7]}_{socket_message[8]}', data)

def start_monitoring(at, *args, **kwargs):
    PeriodicTask.objects.get_or_create(
            clocked  = ClockedSchedule.objects.get_or_create(clocked_time = at)[0], 
            task = 'pnds.tasks.monitor_currency_task', 
            name = f"Monitor '{kwargs['exchange'].upper()}'",
            args = json.dumps(args),
            kwargs = json.dumps(kwargs),
            one_off = True
    )


def monitor_forum(at, forum, pump):
    
    
    PeriodicTask.objects.get_or_create(
            clocked  = ClockedSchedule.objects.get_or_create(clocked_time = at)[0], 
            task = 'pnds.tasks.monitor_messages_for_coin_task',
            name = f'Monitor {forum.get_uri()} for PND id {pump}',
            args = json.dumps([forum.get_uri(), pump]),
            one_off = True
    )

