# Notification Service

This microservice handles anomaly alerts by consuming messages from RabbitMQ, storing anomalies in MongoDB, and broadcasting them to connected clients via WebSocket.

## Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [Running the Service](#running-the-service)
5. [API Endpoints](#api-endpoints)
6. [WebSocket Events](#websocket-events)
7. [Logging](#logging)
8. [Error Handling](#error-handling)

## 1. Overview

The Notification Service listens for anomaly notifications on a RabbitMQ queue (`ANOMALY_QUEUE`), saves them to MongoDB, and emits real-time updates to WebSocket clients under the `/notifications` namespace.

## 2. Prerequisites

* Python 3.9+
* RabbitMQ
* MongoDB

## 3. Configuration

Environment variables or `config.py` must include:

```python
HOST = '0.0.0.0'
PORT = 5003
DEBUG = False

RABBITMQ_HOST = 'rabbitmq'
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'guest'
RABBITMQ_PASS = 'guest'

MONGODB_HOST = 'mongodb'
MONGODB_PORT = 27017
MONGODB_USER = ''      # set if authentication enabled
MONGODB_PASS = ''      # set if authentication enabled
MONGODB_DB   = 'air_pollution'

ANOMALY_QUEUE         = 'anomaly_notification_queue'
USER_NOTIFICATION_QUEUE = 'user_notification_queue'
```

## 4. Running the Service

```bash
python app.py
# or with Docker:
docker build -t notification_service .
docker run -p 5003:5003 --env-file .env notification_service
```

## 5. API Endpoints

### `GET /health`

* **Description:** Health check
* **Response:** `200 OK` with JSON `{ "status": "ok", "service": "notification-service" }`

### `GET /api/v1/pollution/data`

Retrieves pollution records with optional query filters:

* `start_date`, `end_date` (ISO8601 strings)
* `lat`, `lon`, `radius` (km)
* `parameter` (e.g. `PM2.5`)
* `limit`, `skip`

**Response:** `{ status, data, pagination }`

### `GET /api/v1/anomalies`

Retrieves stored anomalies with filters:

* `start_date`, `end_date`
* `severity` (`warning`, `danger`)
* `type` (`threshold_exceeded`, `statistical_anomaly`, `regional_anomaly`)
* `parameter`
* `limit`, `skip`

**Response:** `{ status, data, pagination }`

### `GET /api/v1/heatmap`

Returns aggregated pollution values for map heatmap:

* `parameter` (default `PM2.5`)
* `hours` (default `24`)

**Response:** `{ status, parameter, time_range, data }`

## 6. WebSocket Events

Namespace: `/notifications`

* **Event:** `anomaly_alert`

  * **Payload:** JSON object containing `pollution_data`, `anomaly_info`, `timestamp`

Clients should connect to the namespace and listen for `anomaly_alert` to receive real-time updates.

## 7. Logging

* Uses Python `logging` module at `INFO` level
* Logs connection attempts, errors, and successful broadcasts

## 8. Error Handling

* **MongoDB/RabbitMQ Connection Errors:** Logged and retried
* **Message Processing Errors:** Logged, message requeued
