
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ForumConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.forum = self.scope["url_route"]["kwargs"]["forum"]
        self.group_name = f"{self.forum}"
         
        await self.channel_layer.group_add(
            self.group_name, self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name, self.channel_name
        )
     
    
    async def broadcast(self, event): 
        await self.send(event['message'])

