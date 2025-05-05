#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from flask_cors import CORS
import pika
import json
import threading
import time
import os
import logging
from datetime import datetime, timedelta
import pymongo
from bson.json_util import dumps
from anomaly_detection import detect_anomalies, is_who_threshold_exceeded

import config

# Configure Flask app
app = Flask(__name__)
CORS(app)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create a MongoDB client
def get_mongodb_client():
    try:
        client = pymongo.MongoClient(
            host=config.MONGODB_HOST,
            port=config.MONGODB_PORT,
            username=config.MONGODB_USER,
            password=config.MONGODB_PASS
        )
        return client
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}")
        return None

# Create a RabbitMQ connection
def get_rabbitmq_connection():
    try:
        credentials = pika.PlainCredentials(
            config.RABBITMQ_USER,
            config.RABBITMQ_PASS
        )
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=config.RABBITMQ_HOST,
                port=config.RABBITMQ_PORT,
                credentials=credentials
            )
        )
        return connection
    except Exception as e:
        logger.error(f"RabbitMQ connection error: {e}")
        return None

# Publish an anomaly notification to RabbitMQ
def publish_anomaly(anomaly_data):
    try:
        connection = get_rabbitmq_connection()
        if connection:
            channel = connection.channel()
            channel.queue_declare(queue=config.ANOMALY_QUEUE, durable=True)

            # Convert anomaly data to JSON
            message = json.dumps(anomaly_data)

            # Publish message
            channel.basic_publish(
                exchange='',
                routing_key=config.ANOMALY_QUEUE,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistent
                    content_type='application/json'
                )
            )

            connection.close()
            return True
        return False
    except Exception as e:
        logger.error(f"Error publishing anomaly: {e}")
        return False

# Process incoming pollution data, detect anomalies, store and forward them
def process_pollution_data(data):
    try:
        client = get_mongodb_client()
        if not client:
            logger.error("Unable to connect to MongoDB")
            return False

        db = client[config.MONGODB_DB]
        collection = db.pollution_data

        anomalies = []

        # 1. WHO threshold check
        threshold_anomalies = is_who_threshold_exceeded(data)
        if threshold_anomalies:
            anomalies.extend(threshold_anomalies)

        # 2. Statistical anomaly detection
        # Pull past 24h of data
        end_time = datetime.fromisoformat(data['timestamp'].replace('Z', ''))
        start_time = end_time - timedelta(hours=24)

        historical_data = list(collection.find({
            'latitude': {'$gte': float(data['latitude']) - 0.01, '$lte': float(data['latitude']) + 0.01},
            'longitude': {'$gte': float(data['longitude']) - 0.01, '$lte': float(data['longitude']) + 0.01},
            'timestamp': {'$gte': start_time.isoformat(), '$lte': end_time.isoformat()}
        }).sort('timestamp', pymongo.ASCENDING))

        if historical_data:
            statistical_anomalies = detect_anomalies(data, historical_data)
            if statistical_anomalies:
                anomalies.extend(statistical_anomalies)

        # 3. Insert the new reading
        collection.insert_one(data)

        # 4. If anomalies found, publish notifications
        if anomalies:
            for anomaly in anomalies:
                anomaly_data = {
                    'pollution_data': data,
                    'anomaly_info': anomaly,
                    'timestamp': datetime.utcnow().isoformat()
                }
                publish_anomaly(anomaly_data)
                logger.info(f"Detected anomaly and published: {anomaly['type']}")

        client.close()
        return True

    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return False

# Continuously consume the pollution-data queue
def consume_queue():
    while True:
        try:
            connection = get_rabbitmq_connection()
            if not connection:
                logger.error("RabbitMQ not available, retrying in 5s")
                time.sleep(5)
                continue

            channel = connection.channel()
            channel.queue_declare(queue=config.POLLUTION_DATA_QUEUE, durable=True)

            def callback(ch, method, properties, body):
                try:
                    data = json.loads(body)
                    logger.info(f"New data received: {data.get('id', 'unknown')}")
                    success = process_pollution_data(data)
                    if success:
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    else:
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                except Exception as e:
                    logger.error(f"Consumer callback error: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=config.POLLUTION_DATA_QUEUE, on_message_callback=callback)

            logger.info("Listening to pollution data queue...")
            channel.start_consuming()

        except Exception as e:
            logger.error(f"Queue consumer error: {e}")
            time.sleep(5)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Returns service liveness."""
    return jsonify({"status": "ok", "service": "data-processor"}), 200

# Return summary stats for the last 24h
@app.route('/api/v1/statistics/recent', methods=['GET'])
def get_recent_statistics():
    """Get aggregated pollution statistics for the past 24 hours."""
    try:
        client = get_mongodb_client()
        if not client:
            return jsonify({"status": "error", "message": "DB connection failed"}), 500

        db = client[config.MONGODB_DB]
        collection = db.pollution_data

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)

        pipeline = [
            {
                '$match': {'timestamp': {'$gte': start_time.isoformat(), '$lte': end_time.isoformat()}}
            },
            {
                '$group': {
                    '_id': None,
                    'count': {'$sum': 1},
                    'avg_pm25': {'$avg': '$parameters.PM2.5'},
                    'avg_pm10': {'$avg': '$parameters.PM10'},
                    'avg_no2': {'$avg': '$parameters.NO2'},
                    'avg_so2': {'$avg': '$parameters.SO2'},
                    'avg_o3': {'$avg': '$parameters.O3'},
                    'max_pm25': {'$max': '$parameters.PM2.5'},
                    'max_pm10': {'$max': '$parameters.PM10'},
                    'max_no2': {'$max': '$parameters.NO2'},
                    'max_so2': {'$max': '$parameters.SO2'},
                    'max_o3': {'$max': '$parameters.O3'}
                }
            }
        ]

        results = list(collection.aggregate(pipeline))
        if not results:
            return jsonify({"status": "success", "message": "No data found", "data": {}}), 200

        stats = json.loads(dumps(results[0]))
        client.close()

        return jsonify({
            "status": "success",
            "data": stats,
            "period": {"start": start_time.isoformat(), "end": end_time.isoformat()}
        }), 200

    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Main entry point
if __name__ == '__main__':
    # Start the consumer thread
    consumer_thread = threading.Thread(target=consume_queue)
    consumer_thread.daemon = True
    consumer_thread.start()

    # Run Flask app
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
