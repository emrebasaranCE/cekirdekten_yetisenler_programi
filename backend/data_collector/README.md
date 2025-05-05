# Data Collector Service

A lightweight Flask service that ingests air-pollution readings, validates them, and enqueues them for downstream processing via RabbitMQ.

---

## Contents

1. [Overview](#1-overview)  
2. [Tech Stack](#2-tech-stack)  
3. [Getting Started](#3-getting-started)  
   1. [Prerequisites](#31-prerequisites)  
   2. [Configuration](#32-configuration)  
   3. [Running Locally](#33-running-locally)  
4. [API Endpoints](#4-api-endpoints)  
   1. [Health Check](#41-health-check)  
   2. [Submit Single Reading](#42-submit-single-reading)  
   3. [Submit Batch Readings](#43-submit-batch-readings)  
5. [Payload Schema](#5-payload-schema)  
6. [Environment Variables](#6-environment-variables)  
7. [Error Handling](#7-error-handling)  

---

## 1. Overview

The **Data Collector** service exposes two REST endpoints to receive pollution data:

- **Single-entry**: Accepts one reading at a time  
- **Batch-entry**: Accepts a list of readings  

Each incoming JSON payload is:

1. Validated for required fields and value ranges  
2. Timestamped (if missing)  
3. Published to a RabbitMQ queue (`pollution_data_queue`) for further analysis

---

## 2. Tech Stack

- **Language & Framework:** Python 3.11, Flask  
- **Message Broker:** RabbitMQ (via `pika`)  
- **CORS:** Flask-CORS  

---

## 3. Getting Started

### 3.1 Prerequisites

- Python 3.8+  
- RabbitMQ server  
- `pip`  

### 3.2 Configuration

Copy and edit `config.py` or set the following environment variables:

| Variable                | Default               | Description                             |
|-------------------------|-----------------------|-----------------------------------------|
| `HOST`                  | `0.0.0.0`             | Flask bind address                      |
| `PORT`                  | `5001`                | Flask port                              |
| `DEBUG`                 | `False`               | Flask debug mode                        |
| `RABBITMQ_HOST`         | `rabbitmq`            | RabbitMQ hostname or IP                 |
| `RABBITMQ_PORT`         | `5672`                | RabbitMQ AMQP port                      |
| `RABBITMQ_USER`         | `guest`               | RabbitMQ username                       |
| `RABBITMQ_PASS`         | `guest`               | RabbitMQ password                       |
| `POLLUTION_DATA_QUEUE`  | `pollution_data_queue`| Name of the RabbitMQ queue to publish to|

### 3.3 Running Locally

1. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the service**  
   ```bash
   export HOST=0.0.0.0 PORT=5001
   python app.py
   ```

3. **Verify health check**  
   ```bash
   curl http://localhost:5001/health
   # → {"status":"ok","service":"data-collector"}
   ```

---

## 4. API Endpoints

### 4.1 Health Check

```http
GET /health
```

**Response**  
- `200 OK`  
```json
{"status":"ok","service":"data-collector"}
```

---

### 4.2 Submit Single Reading

```http
POST /api/v1/pollution/data
Content-Type: application/json

{
  "latitude": 40.123456,
  "longitude": 28.654321,
  "parameters": {
    "PM2.5": 42.7,
    "PM10": 60.2,
    "NO2": 15.0
  }
  // "timestamp" optional; service will add if missing
}
```

**Success**  
- `202 Accepted`  
```json
{
  "status":"success",
  "message":"Data received and queued successfully",
  "data_id":"unknown"
}
```

**Client Error**  
- `400 Bad Request` (invalid/missing fields)

---

### 4.3 Submit Batch Readings

```http
POST /api/v1/pollution/batch
Content-Type: application/json

[
  {
    "latitude": 40.1,
    "longitude": 28.6,
    "parameters": {"PM2.5":12.3}
  },
  {
    "latitude": 40.2,
    "longitude": 28.7,
    "parameters": {"SO2":5.4}
  }
]
```

**Success**  
- `207 Multi-Status`  
```json
{
  "status":"completed",
  "results":[
    {"data_id":"unknown","status":"success","message":"Data is valid"},
    {"data_id":"unknown","status":"success","message":"Data is valid"}
  ]
}
```

**Client Error**  
- `400 Bad Request` (payload is not a JSON array)

---

## 5. Payload Schema

| Field        | Type               | Description                                                       |
|--------------|--------------------|-------------------------------------------------------------------|
| `latitude`   | `float`            | −90 to 90                                                        |
| `longitude`  | `float`            | −180 to 180                                                      |
| `timestamp`  | `string` (ISO8601) | Optional; added automatically if omitted                         |
| `parameters` | `object`           | At least one of `"PM2.5"`, `"PM10"`, `"NO2"`, `"SO2"`, `"O3"`, each ≥ 0 numeric |

---

## 6. Environment Variables

See **3.2 Configuration**. You can also supply them via a `.env` file and load with e.g. `python-dotenv`.

---

## 7. Error Handling

- **400** on invalid payload (missing field, out of range, wrong type)  
- **500** on internal errors (RabbitMQ down, unexpected exception)

All error responses follow:

```json
{"status":"error","message":"<description>"}
```

---