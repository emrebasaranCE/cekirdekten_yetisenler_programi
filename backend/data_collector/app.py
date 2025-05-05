#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from flask_cors import CORS
import pika
import json
import os
import logging
from datetime import datetime
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

# Publish a message to the queue
def publish_to_queue(data):
    try:
        connection = get_rabbitmq_connection()
        if connection:
            channel = connection.channel()
            channel.queue_declare(queue=config.POLLUTION_DATA_QUEUE, durable=True)

            # Convert data to JSON
            message = json.dumps(data)

            # Publish to the queue
            channel.basic_publish(
                exchange='',
                routing_key=config.POLLUTION_DATA_QUEUE,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )

            connection.close()
            return True
        return False
    except Exception as e:
        logger.error(f"Error publishing message: {e}")
        return False

# Validate incoming pollution data
def validate_pollution_data(data):
    required_fields = ['latitude', 'longitude', 'timestamp', 'parameters']

    # Check for required fields
    for field in required_fields:
        if field not in data:
            return False, f"Missing field: {field}"

    # Latitude validation
    lat = float(data['latitude'])
    if not (-90 <= lat <= 90):
        return False, "Invalid latitude (must be between -90 and 90)"

    # Longitude validation
    lon = float(data['longitude'])
    if not (-180 <= lon <= 180):
        return False, "Invalid longitude (must be between -180 and 180)"

    # Parameters validation
    valid_params = ['PM2.5', 'PM10', 'NO2', 'SO2', 'O3']
    params = data['parameters']
    if not isinstance(params, dict) or not params:
        return False, "Parameters must be a non-empty dictionary"

    for param, value in params.items():
        if param not in valid_params:
            return False, f"Invalid parameter: {param}. Valid: {', '.join(valid_params)}"
        try:
            val = float(value)
            if val < 0:
                return False, f"Parameter value cannot be negative: {param}"
        except ValueError:
            return False, f"Parameter value must be numeric: {param}"

    return True, "Data is valid"

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Service health check"""
    return jsonify({"status": "ok", "service": "data-collector"}), 200

# Single-entry pollution data endpoint
@app.route('/api/v1/pollution/data', methods=['POST'])
def submit_pollution_data():
    """Endpoint to receive a single pollution data reading"""
    try:
        data = request.json

        # Add timestamp if missing
        if 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat()

        # Validate data
        is_valid, message = validate_pollution_data(data)
        if not is_valid:
            return jsonify({"status": "error", "message": message}), 400

        # Publish to queue
        success = publish_to_queue(data)
        if success:
            return jsonify({
                "status": "success",
                "message": "Data received and queued successfully",
                "data_id": data.get("id", "unknown")
            }), 202
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to queue data. Please try again later."
            }), 500

    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Batch-entry pollution data endpoint
@app.route('/api/v1/pollution/batch', methods=['POST'])
def submit_batch_data():
    """Endpoint to receive a batch of pollution data readings"""
    try:
        data_batch = request.json

        if not isinstance(data_batch, list):
            return jsonify({
                "status": "error",
                "message": "Batch data must be provided as a list"
            }), 400

        results = []
        for data in data_batch:
            # Add timestamp if missing
            if 'timestamp' not in data:
                data['timestamp'] = datetime.utcnow().isoformat()

            is_valid, message = validate_pollution_data(data)
            result = {
                "data_id": data.get("id", "unknown"),
                "status": "success" if is_valid else "error",
                "message": message
            }

            if is_valid:
                if not publish_to_queue(data):
                    result["status"] = "error"
                    result["message"] = "Failed to queue data"

            results.append(result)

        return jsonify({"status": "completed", "results": results}), 207

    except Exception as e:
        logger.error(f"Batch data processing error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Main entry point
if __name__ == '__main__':
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
