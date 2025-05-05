# 1. Rise Through The Ranks

A real-time air-pollution monitoring web application built for Kartaca’s “Cekirdekten Yetişenler” program (2025).  
Currently, the backend microservices are fully implemented—data ingestion, processing, anomaly detection, and alerting are all operational. 
Frontend components (map, charts) are scaffolded but the actual data visualization is still under development.

🔗 [Program Details & Requirements](https://kartaca.com/cekirdekten-yetisenler-programi/usg-gorev-2025/)

---

## 2. Tech Stack

- **Backend:** Python & Flask  
- **Frontend:** JavaScript & Vue.js  
- **Database:** MongoDB  
- **Messaging:** RabbitMQ  

---

## 3. Repository Layout

```
air-pollution-monitoring/
│
├── docker-compose.yml                    
├── README.md                            
├── .gitignore                         
│
├── backend/
│   ├── data_collector/                  
│   │   ├── app.py
│   │   ├── config.py
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   └── requirements.txt
│   │
│   ├── data_processor/                  
│   │   ├── anomaly_detection.py
│   │   ├── app.py
│   │   ├── config.py
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   └── requirements.txt
│   │
│   ├── notification_service/            
│   │   ├── app.py
│   │   ├── config.py
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   └── requirements.txt
│   │
│   └── README.md
│
├── data/
│    └── README.md
│
├── frontend/
│
└── scripts/
    ├── auto-input.sh                     
    └── manual-input.sh                  
```


---

## 4. Project Documentation

For detailed information on each component, please refer to the following README files:

### 4.1 Backend

- [Data Collector, Data Processor and Notification Service](backend/README.md)

### 4.2 Frontend

- [Frontend With Vue.js](frontend/README.md)

### 4.3 Data Handling

- [MongoDB And RabbitMQ](data/README.md)

### 4.4 Manual and Automatic Data Ingestion

- [Bash](scripts/README.md)

---

## 5. Usage

### 5.1 Prerequisites

- Docker (v20.10+)
- Docker Compose (v2.0+)

### 5.2 Running the Stack

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-org/air-pollution-monitoring.git
   cd air-pollution-monitoring

2. **Start all services**
    ```bash
    docker compose up -d

3. **Go to the `localhost:80` on your browser**
    ```
    http://localhost/
    ```
--- 