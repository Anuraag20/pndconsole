from kafka import (
    KafkaAdminClient, 
    KafkaProducer,
    KafkaConsumer
)
from celery.utils.log import get_task_logger

import asyncio
import json
from websockets.asyncio.client import connect
from celery import shared_task
from pndconsole.celery import app

logger = get_task_logger(__name__)

async def monitor_currency(target, pair, freq = 'Min1'):
    
    
    # The producer needs to be created here and cannot be global.
    # This is because of how the memory sharing works in Kafka and gunicorn
        
    producer = KafkaProducer(
        bootstrap_servers = 'localhost:9092',
        value_serializer = lambda value: json.dumps(value).encode('utf-8'),
    )
    async with connect("wss://wbs.mexc.com/ws") as websocket:
        
        setup = {
            "method": "SUBSCRIPTION",
            "params": [f"spot@public.kline.v3.api@{target}{pair}@{freq}"]
        }

        await websocket.send(json.dumps(setup))
        
        prev = {}
        prev_time = 0

        counter = 0
        async for message in websocket:
            
            try:
                data = json.loads(message)
                
                server_time = data['t']
                candlestick = data['d']['k']
                
                time_changed = candlestick['t'] != prev.get('t')

                if time_changed or counter == 30:

                    counter = 0

                    if prev and time_changed:

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

            except KeyError:
                continue

@app.task
def monitor_currency_task():
        
    asyncio.run(monitor_currency('BTC', 'USDT'))

@app.task
def consumer_currency_task():

    consumer = KafkaConsumer(bootstrap_servers = 'localhost:9092', group_id = None)
    consumer.subscribe('market-monitor')
    
    counter = 0
    for message in consumer:
        
        print(message)
        counter += 1

        if counter > 100:

            break

    print('Consumtion complete!')
