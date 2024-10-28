from .models import ScheduledPump

from asgiref.sync import async_to_sync
import asyncio

from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer

from django.conf import settings
from django.utils import timezone

import json

from kafka import ( 
    KafkaProducer,
    KafkaConsumer
)

from market.models import (
        Exchange,
        Coin,
        OHLCVData
)


from pndconsole.celery import app

from typing import Union

logger = get_task_logger(__name__)

async def monitor_currency(exchange, target, pair, topic = 'market-monitor', freq = '1m'):

    
    if not exchange.ccxt_exc.has['watchOHLCV']:
        #TODO: Find a way to handle this 
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

@app.task
def monitor_currency_task(exchange, target, pair):
    
    target = Coin.objects.get(symbol = target)
    pair = Coin.objects.get(symbol = pair)
    exchange = Exchange.objects.get(name = exchange)
    
    with exchange:

        asyncio.run(monitor_currency(exchange, target, pair))

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
