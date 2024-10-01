from django.db import models

# Create your models here.


class Channel(models.Model):

    channel_id = models.TextField(unique = True)
    name = models.TextField()


    def __str__(self):
        return f'{self.name}({self.channel_id})'

class Message(models.Model):

    # Implemnt a field to capture media

    channel = models.ForeignKey(Channel, on_delete = models.CASCADE, related_name = 'messages')
    content = models.TextField()
    sent_at = models.DateTimeField()
    db_added_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f'{self.channel} ({self.sent_at}):{self.content[:30]}'
    




    












