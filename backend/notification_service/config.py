#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# Service configuration
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', 5003))
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
MONGODB_COLLECTION_NOTIFICATIONS = 'notifications'
MONGODB_COLLECTION_ALERTS = 'alerts'

# Queue names
ANOMALY_QUEUE = 'anomaly_notification_queue'
USER_NOTIFICATION_QUEUE = 'user_notification_queue'

# Notification settings
NOTIFICATION_RETENTION_DAYS = 7
ALERT_SEVERITY_LEVELS = ['INFO', 'WARNING', 'DANGER', 'CRITICAL']

# WebSocket configuration
WS_PING_INTERVAL = 30  # saniye
WS_PING_TIMEOUT = 10   # saniye