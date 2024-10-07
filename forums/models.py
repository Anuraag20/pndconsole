from django.conf import settings
from django.contrib.contenttypes.fields import (
        GenericForeignKey,
        GenericRelation
        )
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from llm.detectors import GeminiDetector

from pnds.models import ScheduledPump

detector = GeminiDetector.from_prompt_path(
            api_key = settings.GEMINI_API_KEY,
            coin_prompt_path = settings.COIN_PROMPT_PATH,
            schedule_prompt_path = settings.SCHEDULE_PROMPT_PATH 
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

    class Meta:
        indexes = [
                models.Index(fields = ["content_type", "object_id"]),
                ]


class Forum(models.Model):

    # The identifier that will be used to call relavant APIs
    unique_identifier = models.TextField(unique = True)
    name = models.TextField()
    messages = GenericRelation(Message)

    def __str__(self):
        return f'{self.name}({self.unique_identifier})' 
    class Meta:
        abstract = True


class TelegramChannel(Forum):
    pass


@receiver(post_save, sender = Message, dispatch_uid = "detect_pump_signal")
def detect_pump_signal(sender, instance, created, **kwargs):
    if created:
        print(detector.get_info(instance.content))
