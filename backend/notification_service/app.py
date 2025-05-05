#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import pika
import json
import threading
import time
import os
import logging
from datetime import datetime, timedelta, timezone
import pymongo
from bson.json_util import dumps
from bson.objectid import ObjectId
import config

# Initialize Flask application
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Logging configuration
tlogging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Function to get MongoDB client
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

# Function to get RabbitMQ connection
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

# Broadcast anomaly notifications over WebSocket
def broadcast_anomaly(anomaly_data):
    try:
        socketio.emit('anomaly_alert', anomaly_data, namespace='/notifications')
        logger.info(f"Anomaly notification broadcasted: {anomaly_data.get('anomaly_info', {}).get('type')}")
    except Exception as e:
        logger.error(f"WebSocket broadcast error: {e}")

# Consume anomaly queue and process messages
def consume_anomaly_queue():
    while True:
        try:
            connection = get_rabbitmq_connection()
            if not connection:
                logger.error("Cannot connect to RabbitMQ. Retrying in 5 seconds...")
                time.sleep(5)
                continue

            channel = connection.channel()
            channel.queue_declare(queue=config.ANOMALY_QUEUE, durable=True)

            def callback(ch, method, properties, body):
                try:
                    anomaly_data = json.loads(body)
                    logger.info(f"Received anomaly: {anomaly_data.get('anomaly_info', {}).get('type')}")

                    # Save anomaly to MongoDB
                    client = get_mongodb_client()
                    if client:
                        db = client[config.MONGODB_DB]
                        db.anomalies.insert_one(anomaly_data)
                        client.close()

                    # Broadcast via WebSocket
                    broadcast_anomaly(anomaly_data)

                    # Acknowledge message
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Error processing anomaly: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=config.ANOMALY_QUEUE, on_message_callback=callback)
            logger.info("Listening for anomalies on RabbitMQ...")
            channel.start_consuming()

        except Exception as e:
            logger.error(f"Anomaly consumer error: {e}")
            time.sleep(5)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "service": "notification-service"}), 200

# Retrieve pollution data with optional filters
@app.route('/api/v1/pollution/data', methods=['GET'])
def get_pollution_data():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        radius = request.args.get('radius')
        parameter = request.args.get('parameter')
        limit = int(request.args.get('limit', 1000))
        skip = int(request.args.get('skip', 0))

        client = get_mongodb_client()
        if not client:
            return jsonify({"status": "error", "message": "Failed to connect to database"}), 500

        db = client[config.MONGODB_DB]
        collection = db.pollution_data
        query = {}

        if start_date or end_date:
            query['timestamp'] = {}
            if start_date:
                query['timestamp']['$gte'] = start_date
            if end_date:
                query['timestamp']['$lte'] = end_date

        if lat and lon and radius:
            lat_f = float(lat)
            lon_f = float(lon)
            rad_f = float(radius)
            lat_delta = rad_f / 111.0
            lon_delta = rad_f / (111.0 * abs(math.cos(math.radians(lat_f))))
            query['latitude'] = {'$gte': lat_f - lat_delta, '$lte': lat_f + lat_delta}
            query['longitude'] = {'$gte': lon_f - lon_delta, '$lte': lon_f + lon_delta}

        if parameter:
            query[f'parameters.{parameter}'] = {'$exists': True}

        results = list(collection.find(query)
                      .sort('timestamp', pymongo.DESCENDING)
                      .skip(skip)
                      .limit(limit))
        total = collection.count_documents(query)
        json_data = json.loads(dumps(results))
        client.close()

        return jsonify({
            "status": "success",
            "data": json_data,
            "pagination": {"total": total, "limit": limit, "skip": skip}
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving pollution data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Retrieve anomalies with optional filters
@app.route('/api/v1/anomalies', methods=['GET'])
def get_anomalies():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        severity = request.args.get('severity')
        anomaly_type = request.args.get('type')
        parameter = request.args.get('parameter')
        limit = int(request.args.get('limit', 100))
        skip = int(request.args.get('skip', 0))

        client = get_mongodb_client()
        if not client:
            return jsonify({"status": "error", "message": "Failed to connect to database"}), 500

        db = client[config.MONGODB_DB]
        collection = db.anomalies
        query = {}

        if start_date or end_date:
            query['timestamp'] = {}
            if start_date:
                query['timestamp']['$gte'] = start_date
            if end_date:
                query['timestamp']['$lte'] = end_date

        if severity:
            query['anomaly_info.severity'] = severity
        if anomaly_type:
            query['anomaly_info.type'] = anomaly_type
        if parameter:
            query['anomaly_info.parameter'] = parameter

        results = list(collection.find(query)
                      .sort('timestamp', pymongo.DESCENDING)
                      .skip(skip)
                      .limit(limit))
        total = collection.count_documents(query)
        json_data = json.loads(dumps(results))
        client.close()

        return jsonify({
            "status": "success",
            "data": json_data,
            "pagination": {"total": total, "limit": limit, "skip": skip}
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving anomalies: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Retrieve heatmap data for map visualization
@app.route('/api/v1/heatmap', methods=['GET'])
def get_heatmap_data():
    try:
        parameter = request.args.get('parameter', 'PM2.5')
        hours = int(request.args.get('hours', 24))

        client = get_mongodb_client()
        if not client:
            return jsonify({"status": "error", "message": "Failed to connect to database"}), 500

        db = client[config.MONGODB_DB]
        collection = db.pollution_data
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        pipeline = [
            { '$match': { 'timestamp': { '$gte': start_time.isoformat(), '$lte': end_time.isoformat() }, f"parameters.{parameter}": {'$exists': True} } },
            { '$group': { '_id': {'latitude': '$latitude', 'longitude': '$longitude'}, 'value': {'$avg': {'$toDouble': f"$parameters.{parameter}"}}, 'count': {'$sum': 1} } },
            { '$project': { '_id': 0, 'latitude': '$_id.latitude', 'longitude': '$_id.longitude', 'value': 1, 'count': 1 } }
        ]

        results = list(collection.aggregate(pipeline))
        json_data = json.loads(dumps(results))
        client.close()

        return jsonify({
            "status": "success",
            "parameter": parameter,
            "time_range": {"start": start_time.isoformat(), "end": end_time.isoformat()},
            "data": json_data
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving heatmap data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# WebSocket event handlers
@socketio.on('connect', namespace='/notifications')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")

@socketio.on('disconnect', namespace='/notifications')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

# Main entry point
if __name__ == '__main__':
    # Start anomaly consumer thread
    consumer_thread = threading.Thread(target=consume_anomaly_queue)
    consumer_thread.daemon = True
    consumer_thread.start()

    # Run Flask-SocketIO server
    socketio.run(
        app,
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG,
        allow_unsafe_werkzeug=True  # Development only
    )
