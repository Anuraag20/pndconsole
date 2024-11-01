from asgiref.sync import async_to_sync


from django.conf import settings
from django.contrib.contenttypes.fields import (
        GenericForeignKey,
        GenericRelation
        )
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils import timezone
from llm.detectors import GeminiDetector

from pnds.models import ScheduledPump
from pandas import to_datetime
from channels.layers import get_channel_layer

import typing_extensions as typing
import json

from market.models import (
        Exchange, 
        Coin
)

layer = get_channel_layer()

class Response(typing.TypedDict):

    scheduled_at: str
    exchanges: list[str]
    coin: str
    pair: str
    guess: bool

detector = GeminiDetector.from_prompt_path(
            api_key = settings.GEMINI_API_KEY,
            path = settings.SCHEDULE_PROMPT_PATH,
            response_schema = Response
        )

class Message(models.Model):

    # TODO: Implemnt a field to capture media

    content_type = models.ForeignKey(ContentType, on_delete = models.CASCADE)
    object_id = models.PositiveIntegerField()
    forum = GenericForeignKey("content_type", "object_id")

    content = models.TextField()
    sent_at = models.DateTimeField()
    db_added_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f'{self.forum.name} - ({self.sent_at}): {self.content[:30]}'
    
    @property
    def forum_cls_name(self) -> str:
        return self.forum.__class__.__name__.lower()

    class Meta:
        indexes = [
                models.Index(fields = ["content_type", "object_id"]),
                ]


class Forum(models.Model):

    # The identifier that will be used to call relavant APIs
    unique_identifier = models.TextField(unique = True)
    name = models.TextField()
    messages = GenericRelation(Message, related_query_name = '%(class)s')

    def __str__(self):
        return f'{self.name}({self.unique_identifier})' 

    def get_uri(self):
        return f'{self.__class__.__name__.lower()}_{self.unique_identifier}'

    class Meta:
        abstract = True


class TelegramChannel(Forum):
    pass
    

@receiver(post_save, sender = Message, dispatch_uid = "detect_pump_signal")
def detect_pump_signal(sender, instance, created, **kwargs):
    if created:
        
        result = json.loads(detector.prompt([instance.content, f'Message received at: {instance.sent_at}']))

        if result != {}:

            if result.get('exchanges') and result.get('scheduled_at') and result.get('pair'):

                    exchanges = []
                    for exchange in  result.get('exchanges'):
                        exchanges.append( Exchange.objects.get_or_create( name = exchange.replace('.com', '').lower() )[0] )

                    pair = Coin.objects.get_or_create(symbol = result.get('pair'))[0]
                    scheduled_at = to_datetime(result.get('scheduled_at'))
                       


                    prev_pumps = ScheduledPump.objects.filter(**{
                        f'message__{instance.forum_cls_name}': instance.forum,
                        'scheduled_at': scheduled_at
                    })

                    if not prev_pumps.exists():

                            sp = ScheduledPump.objects.create(
                                message = instance, 
                                pair = pair,
                                scheduled_at = scheduled_at,
                                pair_guessed = result.get('guessed', False)
                            )
                            sp.exchanges.add(*exchanges)
                    else:
                        print('previous pump detected!')
        group = f'{instance.forum_cls_name}_{instance.forum.unique_identifier}'
        data = {
                'type': 'broadcast',
                'message': instance.content
                }
        async_to_sync(layer.group_send)(group, data) 
