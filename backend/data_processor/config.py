#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# Service configuration
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5002))
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# RabbitMQ configuration
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'guest')

# MongoDB configuration
MONGODB_HOST = os.environ.get('MONGODB_HOST', 'mongodb')
MONGODB_PORT = int(os.environ.get('MONGODB_PORT', 27017))
MONGODB_USER = os.environ.get('MONGODB_USER', '')
MONGODB_PASS = os.environ.get('MONGODB_PASS', '')
MONGODB_DB = os.environ.get('MONGODB_DB', 'air_pollution')

# Queue name
POLLUTION_DATA_QUEUE = 'pollution_data_queue'
ANOMALY_QUEUE = 'anomaly_notification_queue'