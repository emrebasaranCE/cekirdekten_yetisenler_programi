# Backend: Python & Flask

Leveraging Python and Flask for its simplicity and my familiarity, the backend is split into three focused microservices. Each service has its own responsibility and can be run, scaled, and tested independently.

---

## Backend Services

| Service               | Description                                                                                                             | Docs                                                   |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|
| **Data Collector**    | Receives incoming pollution readings via REST, validates payloads, and enqueues them on RabbitMQ for further processing. | [View Docs](backend/data_collector/README.md)          |
| **Data Processor**    | Consumes raw readings from RabbitMQ, stores them in MongoDB, runs WHO-based & statistical/regional anomaly detection, and publishes anomalies. | [View Docs](backend/data_processor/README.md)          |
| **Notification Service** | Listens for anomalies on RabbitMQ, persists alerts, and pushes real-time notifications over WebSocket to connected clients. | [View Docs](backend/notification_service/README.md)    |
