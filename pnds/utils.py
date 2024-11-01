from django_celery_beat.models import (
        PeriodicTask, 
        ClockedSchedule
)

import json


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

