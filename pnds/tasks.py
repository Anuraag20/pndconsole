from .models import ScheduledPump

import asyncio

from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer

from django.conf import settings
from django.utils import timezone

from django.db import IntegrityError


from llm.detectors import GeminiDetector

from market.models import (
        Exchange,
        Coin,
        OHLCVData
)

from pndconsole.celery import app

from websockets.asyncio.client import connect

from .utils import (
        create_candle,
        get_detector
)
from asgiref.sync import sync_to_async


logger = get_task_logger(__name__)
 
async def monitor_currency(exchange, target, pair, topic = 'market-monitor', freq = '1m'):        
    #TODO: Find a way to handle this 
    if not exchange.ccxt_exc.has['watchOHLCV']:
        logger.error(f'Exchange {exchange} does not have the watchOHLCV method')
        return

    value_serializer = lambda value: [
                    settings.CELERY_STREAMING_VERSION, 
                    exchange.id, 
                    target.id, 
                    pair.id, 
                    freq,
                    *value
                ]
    

    layer = get_channel_layer()

    # Timestamp, Open, High, Low, Close, Volume
    prev = [0, 0, 0, 0, 0, 0]

    counter = 0

    start_time = timezone.now()
    
    init_candles = await exchange.fetch_ohlcv(
                target,
                pair,
                timeframe = freq, 
            )
   
    for candle in init_candles:
        await sync_to_async(create_candle)(candle, serializer = value_serializer, layer = layer)

    detector = get_detector(init_candles)

    while True:  
        data = await exchange.watch_ohlcv(target, pair, timeframe = freq) 
       
        candlestick = data[-1]  # Get the most recent value in case two trades get executed at the same time

        time_changed = candlestick[0] != prev[0]

        if time_changed or counter == settings.RESEND_CURRENT_MIN_AFTER:
            counter = 0

            if prev[0] != 0 and time_changed:
                await sync_to_async(create_candle)(prev, serializer = value_serializer, layer = layer, detector = detector)
                logger.info('Sent previous')


            await sync_to_async(create_candle)(candlestick, serializer = value_serializer, layer = layer, detector = detector)
            logger.info('Sent recent')
        
        else:
                counter += 1

        prev = candlestick
        
        if timezone.now() - start_time > settings.STOP_PRODUCING_AFTER:
            logger.info('Done producing!')
            break


async def monitor_messages(uri, scheduled_pump: ScheduledPump):
    

    detector = GeminiDetector.from_prompt_path(
            api_key = settings.GEMINI_API_KEY,
            path = settings.COIN_PROMPT_PATH
        )
    
    async with connect(settings.WEB_SOCKET_BASE_URL + 'ws/forum/' + uri + '/') as websocket:
            messages = []
            async for message in websocket:

                    messages.append(message)

                    response = ''.join(c for c in detector.prompt(messages) if c.isalpha())
                    logger.info(f'COIN DETECTOR: {response}')
                    if response != '' and not ' ' in response:

                        coin = await Coin.objects.aget_or_create(symbol = response)
                        coin = coin[0]
                        scheduled_pump.target = coin
                        await scheduled_pump.asave()

                        break


                
@app.task
def monitor_currency_task(exchange: str, target: int, pair: int, topic: str, freq = '1m'):

    target = Coin.objects.get(id = target)
    pair = Coin.objects.get(id = pair)
    exchange = Exchange.objects.get(name = exchange)
    
    with exchange:

        asyncio.run(monitor_currency(exchange, target, pair, topic, freq))


    
    


@app.task
def monitor_messages_for_coin_task(uri: str, scheduled_pump: int): 
        
        scheduled_pump = ScheduledPump.objects.get(id = scheduled_pump)
        asyncio.run(monitor_messages(uri, scheduled_pump)) 
