import json
from channels.generic.websocket import AsyncWebsocketConsumer


class PNDConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.coin = self.scope["url_route"]["kwargs"]["coin"]
        self.coin_group_name = f"coin_{self.coin}"
        
        await self.channel_layer.group_add(
            self.coin_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        
        await self.channel_layer.group_discard(
            self.coin_group_name, self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        data = text_data_json["message"]
         
        # Send message to room group
        await self.channel_layer.group_send(
                self.coin_group_name, {"type": "market_data", "message": data}
        )

    # Receive message from room group
    async def market_data(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))
