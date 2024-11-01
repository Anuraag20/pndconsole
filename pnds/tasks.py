from .models import ScheduledPump

from asgiref.sync import async_to_sync
import asyncio

from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer

from django.conf import settings
from django.dispatch import receiver
from django.utils import timezone

import json

from kafka import ( 
    KafkaProducer,
    KafkaConsumer
)

from llm.detectors import GeminiDetector

from market.models import (
        Exchange,
        Coin,
        OHLCVData
)

from pndconsole.celery import app

from websockets.asyncio.client import connect


logger = get_task_logger(__name__)

async def monitor_currency(exchange, target, pair, topic = 'market-monitor', freq = '1m'):        
    #TODO: Find a way to handle this 
    if not exchange.ccxt_exc.has['watchOHLCV']:
        logger.error(f'Exchange {exchange} does not have the watchOHLCV method')
        return

    # The producer needs to be created here and cannot be global.
    # This is because of how the memory sharing works in Kafka and gunicorn
    producer = KafkaProducer(
            bootstrap_servers = 'localhost:9092',
            value_serializer = lambda value: json.dumps([
                    settings.STREAMING_VERSION, 
                    exchange.id, 
                    target.id, 
                    pair.id, 
                    *value
                ]).encode('utf-8'),
    )

    # TODO: Keep track of data for each exchange separately
    # IDEA: watch_ohlcv_for_symbols and exchange as a key

    # Timestamp, Open, High, Low, Close, Volume
    prev = [0, 0, 0, 0, 0, 0]
    prev_time = 0

    counter = 0

    start_time = timezone.now()
    
    init_candles = await exchange.fetch_ohlcv(
                target,
                pair,
                timeframe = '1m', 
            )
    
    for candle in init_candles: 
        producer.send(
                topic = topic,
                value = candle,
                timestamp_ms = round(timezone.now().timestamp() * 1000)
            )
 
    while True:  
        data = await exchange.watch_ohlcv(target, pair, timeframe = freq) 
       
        server_time = round(timezone.now().timestamp() * 1000)
        candlestick = data[-1]  # Get the most recent value in case two trades get executed at the same time

        time_changed = candlestick[0] != prev[0]

        if time_changed or counter == settings.RESEND_CURRENT_MIN_AFTER:
            counter = 0

            if prev[0] != 0 and time_changed:
                producer.send(
                    topic = topic,
                    value = prev,
                    timestamp_ms = prev_time
                )
                logger.info('Sent previous')

            producer.send(
                topic = topic,
                value = candlestick,
                timestamp_ms = server_time
            )

            logger.info('Sent recent')
        
        else:
                counter += 1

        prev = candlestick
        prev_time = server_time
        
        if timezone.now() - start_time > settings.STOP_PRODUCING_AFTER:
            logger.info('Done producing!')
            break


async def monitor_messages(uri, scheduled_pump: ScheduledPump):
    

    detector = GeminiDetector.from_prompt_path(
            api_key = settings.GEMINI_API_KEY,
            path = settings.COIN_PROMPT_PATH
        )
    
    async with connect(settings.WEB_SOCKET_BASE_URL + 'ws/forum/' + uri + '/') as websocket:
            import re        
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
def monitor_currency_task(exchange: str, target: int, pair: int, topic: str):

    target = Coin.objects.get(id = target)
    pair = Coin.objects.get(id = pair)
    exchange = Exchange.objects.get(name = exchange)
    
    with exchange:

        asyncio.run(monitor_currency(exchange, target, pair, topic))

@app.task
def consumer_currency_task(topic = 'market-monitor'):
    consumer = KafkaConsumer(
            bootstrap_servers = 'localhost:9092', 
            group_id = None,
            value_deserializer = lambda val: json.loads(val.decode("utf-8"))
            
    )
    consumer.subscribe(topic)
    
    layer = get_channel_layer()
    start_time = timezone.now()

    for message in consumer:
            
        candle = OHLCVData.from_stream( 
                    data = message.value,
                    received_at = message.timestamp,
                    is_pump = False,
                    is_pump_non_ml = False
                ) 
        data = {
                    'type': 'market_data',
                    'message': [candle.get_candle()]
                }
        async_to_sync(layer.group_send)('BTC_USDT', data)

        if timezone.now() - start_time > settings.STOP_CONSUMING_AFTER:
            logger.info('Im outta here!')
            break  


    logger.info('Consumption complete!')


@app.task
def monitor_messages_for_coin_task(uri: str, scheduled_pump: int): 
        
        scheduled_pump = ScheduledPump.objects.get(id = scheduled_pump)
        asyncio.run(monitor_messages(uri, scheduled_pump)) 
