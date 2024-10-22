from asgiref.sync import (
        async_to_sync,
        sync_to_async,
)
import asyncio

import ccxt.pro as ccxt
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer

from datetime import timedelta
from django.conf import settings
from django.utils import timezone

import json

from kafka import ( 
    KafkaProducer,
    KafkaConsumer
)

from market.models import (
        Coin,
        Exchange,
        OHLCVData,
)

from pndconsole.celery import app



logger = get_task_logger(__name__)



async def monitor_currency(exchange, target, pair, freq = '1m'):

    
    if not exchange.ccxt_exc.has['watchOHLCV']:
        #TODO: Find a way to handle this 
        logger.error(f'Exchange {exchange} does not have the watchOHLCV method')
        return

    # The producer needs to be created here and cannot be global.
    # This is because of how the memory sharing works in Kafka and gunicorn
    producer = KafkaProducer(
            bootstrap_servers = 'localhost:9092',
            value_serializer = lambda value: json.dumps(value).encode('utf-8'),
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
        
        await OHLCVData.objects.aget_or_create(
            exchange = exchange,
            coin = target,
            pair = pair,
            market_time = timezone.make_aware( timezone.datetime.fromtimestamp(candle[0]/1000) ),
            defaults = {
                'open': candle[1],
                'high': candle[2],
                'low': candle[3],
                'close': candle[4],
                'volume': candle[5],
            }
        )

    while True: 
        
        data = await exchange.watch_ohlcv(f'{target}/{pair}', timeframe = freq) 
       
        server_time = round(timezone.now().timestamp() * 1000)
        candlestick = data[-1]  # Get the most recent value in case two trades get executed at the same time

        time_changed = candlestick[0] != prev[0]

        if time_changed or counter == settings.RESEND_CURRENT_MIN_AFTER:
            counter = 0

            if prev[0] != 0 and time_changed:
                producer.send(
                    topic = 'market-monitor',
                    value = prev,
                    timestamp_ms = prev_time
                )
                logger.info('Sent previous')

            producer.send(
                topic = 'market-monitor',
                value = candlestick,
                timestamp_ms = server_time
            )

            logger.info('Sent recent')
        
        else:
                counter += 1

        prev = candlestick
        prev_time = server_time
        
        if timezone.now() - start_time > settings.STOP_MONITORING_AFTER:
            break

@app.task
def monitor_currency_task():

    target = Coin.objects.get(symbol = 'BTC')
    pair = Coin.objects.get(symbol = 'USDT')
    exchange = Exchange.objects.get(name = 'mexc')
    
    with exchange:

        asyncio.run(monitor_currency(exchange, target, pair))

@app.task
def consumer_currency_task():

    consumer = KafkaConsumer(
            bootstrap_servers = 'localhost:9092', 
            group_id = None,
            value_deserializer = lambda val: json.loads(val.decode("utf-8"))
            
    )
    consumer.subscribe('market-monitor')
    
    counter = 0

    layer = get_channel_layer()
    for message in consumer:
        
        
        counter += 1
       
        data = {
            "type": "market_data",
            "message": message.value
        }
        async_to_sync(layer.group_send)('coin_BTCUSDT', data)

        if counter > 100:

            break

    logger.info('Consumption complete!')
