import json
from channels.generic.websocket import AsyncWebsocketConsumer
from market.models import OHLCVData
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone


class PNDConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.target = self.scope["url_route"]["kwargs"]["target"]
        self.pair = self.scope["url_route"]["kwargs"]["pair"]
        self.group_name = f"{self.target}_{self.pair}"
        
        await sync_to_async(print)(self.target, self.pair)
        
        await self.channel_layer.group_add(
            self.group_name, self.channel_name
        )
        
        self.initialized = False
        await self.accept()
    
    
    def get_initial_data(self):
        time = timezone.now() - (settings.FETCH_PREVIOUS_DEFAULT + settings.STOP_CONSUMING_AFTER)
        data = OHLCVData.objects.filter(
                    coin__symbol = self.target,
                    pair__symbol = self.pair,
                    market_time__gte = time
                ).get_candles()
        print(list(data))
        return list(data)


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name, self.channel_name
        )


    async def receive(self, text_data):
        
        data = json.loads(text_data)
        
        if data["type"] == "initialize":
            await self.initialize()

    
    async def initialize(self):
        data = await sync_to_async(self.get_initial_data)()
        self.initialized = True
        await self.send(text_data = json.dumps(data))



    async def market_data(self, event):
        message = event["message"]
        print(message)
        if self.initialized:
            await self.send(text_data = json.dumps(message))

