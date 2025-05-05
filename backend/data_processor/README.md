# Data Processor Service

A Flask-based microservice that consumes raw air-pollution readings from RabbitMQ, persists them to MongoDB, applies WHO threshold checks and statistical/regional anomaly detection, and publishes any detected anomalies back onto a RabbitMQ queue for downstream alerting.

---

## Contents

1. [Overview](#1-overview)  
2. [Configuration](#2-configuration)  
3. [Core Components](#3-core-components)  
   1. [get_rabbitmq_connection()](#31-get_rabbitmq_connection)  
   2. [get_mongodb_client()](#32-get_mongodb_client)  
   3. [publish_anomaly()](#33-publish_anomaly)  
   4. [process_pollution_data()](#34-process_pollution_data)  
   5. [consume_queue()](#35-consume_queue)  
4. [REST API Endpoints](#4-rest-api-endpoints)  
   1. [GET /health](#41-get-health)  
   2. [GET /api/v1/statistics/recent](#42-get-apiv1statisticsrecent)  
5. [Anomaly Detection Module](#5-anomaly-detection-module)  
   1. [WHO Thresholds](#51-who-thresholds)  
   2. [Statistical Anomalies](#52-statistical-anomalies)  
   3. [Regional Anomalies](#53-regional-anomalies)  
6. [Running & Deployment](#6-running--deployment)  
7. [Troubleshooting](#7-troubleshooting)  

---


## 1. Overview

The **Data Processor** microservice consumes raw pollution readings from RabbitMQ, applies WHO-based and statistical/regional anomaly detection, stores all readings in MongoDB, and forwards any detected anomalies to a dedicated RabbitMQ queue. It also exposes a REST endpoint to deliver summary statistics for the last 24 hours.

---

## 2. Configuration

All service settings live in `config.py`. Key variables:

- **HOST, PORT, DEBUG**: Flask server bind and debug mode  
- **RABBITMQ_HOST, …_PORT, …_USER, …_PASS**: RabbitMQ connection parameters  
- **POLLUTION_DATA_QUEUE**: incoming raw data queue name  
- **ANOMALY_QUEUE**: outgoing anomaly notifications queue  
- **MONGODB_HOST, …_PORT, …_USER, …_PASS, …_DB**: MongoDB connection parameters  

---

## 3. Core Components

### 3.1 `get_rabbitmq_connection()`

Opens a blocking connection to RabbitMQ using **pika**, returns a `BlockingConnection` or `None` on failure.

### 3.2 `get_mongodb_client()`

Creates a **pymongo** `MongoClient` connected to the configured database, or returns `None` on error.

### 3.3 `publish_anomaly(anomaly_data)`

Serializes a Python `dict` to JSON and publishes it to `ANOMALY_QUEUE` (durable, persistent).

### 3.4 `process_pollution_data(data)`

1. **Threshold check**: calls `is_who_threshold_exceeded(data)`  
2. **Statistical detection**: fetches the last 24 hours of readings for the same location and calls `detect_anomalies(data, historical_data)`  
3. **Storage**: inserts the new reading into `pollution_data` collection  
4. **Notification**: for each anomaly, constructs a wrapper message and calls `publish_anomaly(...)`

Returns `True` if processing succeeded, else `False`.

### 3.5 `consume_queue()`

Long-running thread that:

- Connects to RabbitMQ  
- Consumes messages from `POLLUTION_DATA_QUEUE` one at a time  
- Parses incoming JSON, calls `process_pollution_data`  
- Acknowledges or re-queues upon success/failure  
- Retries the connection on error every 5 seconds

---

## 4. REST API Endpoints

### 4.1 `GET /health`

- **Response**: `200 OK`  
  ```json
  { "status": "ok", "service": "data-processor" }
  ```

### 4.2 `GET /api/v1/statistics/recent`

- **Purpose**: Aggregates all readings in the last 24 hours  
- **Pipeline**:  
  ```js
  [
    { $match: { timestamp: { $gte: ISO(start), $lte: ISO(end) } } },
    {
      $group: {
        _id: null,
        count: { $sum: 1 },
        avg_pm25: { $avg: "$parameters.PM2.5" },
        …
        max_o3: { $max: "$parameters.O3" }
      }
    }
  ]
  ```
- **Response**:  
  ```json
  {
    "status": "success",
    "data": { "count":…, "avg_pm25":…, …, "max_o3":… },
    "period": { "start": …, "end": … }
  }
  ```
- **Errors**: returns `500` with `{"status":"error","message":…}` if anything fails.

---

## 5. Anomaly Detection Module

File: `anomaly_detection.py`

### 5.1 WHO Thresholds

- **WHO_THRESHOLDS**: 24 h/8 h guideline limits  
- **DANGEROUS_THRESHOLDS**: 2× WHO values

#### `is_who_threshold_exceeded(data)`

- Iterates each `parameters[param]` in the incoming reading  
- Flags if value > WHO threshold (`warning`) or > dangerous threshold (`danger`)  
- Returns a list of anomaly records:
  ```json
  {
    "type": "threshold_exceeded",
    "parameter": "PM2.5",
    "value": 20.1,
    "threshold": 15.0,
    "dangerous_threshold": 30.0,
    "severity": "warning",
    "message": "PM2.5 exceeded WHO threshold (20.10 > 15.00)"
  }
  ```

### 5.2 Statistical Anomalies

#### `calculate_z_score(value, series)`

- Computes (value – mean)/std, returns 0 if <2 points or std=0.

#### `detect_anomalies(current_data, historical_data)`

1. **Gather** last 24 h values for each pollutant at that location  
2. **Compute** Z-score and percent change from mean  
3. **Flag** if |Z| > 3 or |Δ%| > 50% (`warning` or `danger`)  
4. **Append** a record:
   ```json
   {
     "type": "statistical_anomaly",
     "parameter": "NO2",
     "value": 80.0,
     "average": 40.2,
     "z_score": 4.5,
     "percent_change": 98.5,
     "severity": "danger",
     "message": "NO2 98.5% increase"
   }
   ```
5. **Call** `detect_regional_anomalies(...)` to include spatial outliers

### 5.3 Regional Anomalies

#### `haversine_distance(lat1,lon1,lat2,lon2)`

- Computes great-circle distance in km.

#### `detect_regional_anomalies(current_data, historical_data, anomalies)`

- Considers readings within a 25 km radius in the past 6 hours  
- Computes regional means; flags if current deviates by > 75% (`warning` <150% or `danger` ≥150%)  
- Avoids duplicates if already reported

---

## 6. Running & Deployment

1. **Build & start** (assumes `docker-compose.yml` in root):
   ```bash
   docker-compose up -d --build data_processor
   ```
2. **Confirm** logs:
   ```bash
   docker-compose logs -f data_processor
   ```
3. **Test** the stats endpoint:
   ```bash
   curl http://localhost:5002/api/v1/statistics/recent
   ```

---

## 7. Troubleshooting

- **RabbitMQ connectivity**: check `RABBITMQ_HOST`, `…_PORT`  
- **MongoDB auth**: ensure user/password match `MONGO_INITDB_ROOT_*` envs  
- **Time parsing**: timestamps must be ISO-formatted (with trailing `Z`)  

