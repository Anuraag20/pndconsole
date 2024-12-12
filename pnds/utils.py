
from django_celery_beat.models import (
        PeriodicTask, 
        ClockedSchedule
)

import json
import pandas as pd
import numpy as np
from adtk.detector import InterQuartileRangeAD
from django.utils import timezone


def _detector(model, x, y):

    input = pd.Series([y], index = [timezone.make_aware( timezone.datetime.fromtimestamp(x/1000) )])
    return bool(model.predict(input).iloc[0])

def get_detector(data):
    data = np.array(data)

    index = [timezone.make_aware( timezone.datetime.fromtimestamp(t/1000) ) for t in data[:, 5].astype(int)]
    input = pd.Series(data[:, 9].astype(float), index = index)
    iqr = InterQuartileRangeAD(c = 1.5)
    iqr.fit(input)

    return lambda x, y: _detector(iqr, x, y)


def start_monitoring(at, *args, **kwargs):
    PeriodicTask.objects.get_or_create(
            clocked  = ClockedSchedule.objects.get_or_create(clocked_time = at)[0], 
            task = 'pnds.tasks.monitor_currency_task', 
            name = f"Monitor '{kwargs['exchange'].upper()}' for {kwargs['topic']}",
            args = json.dumps(args),
            kwargs = json.dumps(kwargs),
            one_off = True
    )


def start_consuming(at, topic): 
    PeriodicTask.objects.get_or_create(
            clocked  = ClockedSchedule.objects.get_or_create(clocked_time = at)[0], 
            task = 'pnds.tasks.consumer_currency_task', 
            name = f"Consumer for {topic}",
            args = json.dumps([topic]),
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

