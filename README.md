# Contents

- [1. Rise Through The Ranks](#1-rise-through-the-ranks)  
- [2. Tech Stack](#2-tech-stack)  
- [3. Project Layout](#3-project-layout)  
  - [1. Repository Layout](#31-repository-layout)
  - [2. Docker Compose](#32-docker-compose)
    - [1. Restart & Healthchecks](#321-restart--healthchecks)
- [4. Project Documentation](#4-project-documentation)  
  - [4.1 Backend](#41-backend)  
  - [4.2 Frontend](#42-frontend)  
  - [4.3 Data Handling](#43-data-handling)  
  - [4.4 Manual and Automatic Data Ingestion](#44-manual-and-automatic-data-ingestion)  
- [5. Usage](#5-usage)  
  - [5.1 Prerequisites](#51-prerequisites)  
  - [5.2 Running the Stack](#52-running-the-stack)  

---

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

## 3. Project Layout

### 3.1. Repository Layout

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

### 3.2. Docker Compose

This project's entire stack is wired up via docker-compose.yml (version 3.8). Below is a summary of the key settings — please refer to the top‐level docker-compose.yml for the full file.

#### 3.2.1. Restart & Healthchecks

Every service is configured with restart: always so that Docker will automatically bring it back up if it crashes. In addition:
  - **rabbitmq**
    - **Healthcheck**: CMD rabbitmqctl status
    - **Ports**: 5672 (AMQP), 15672 (management UI)
  - **mongodb**
    - **Healthcheck**: 
      ```bash
      test: ["CMD-SHELL", "mongosh --quiet --eval \"db.adminCommand({ ping: 1 })\" -u root -p rootpassword --authenticationDatabase admin || exit 1"]
      ```
      **Ports**:27017
  - **data_collector**
    - **Healthcheck**: `CMD curl -f http://localhost:5001/health`
    - **Ports**: 5001
  - **data_processor**
    - **Healthcheck**: `CMD curl -f http://localhost:5002/health`
    - **Ports**: 5002
  - **notification_service**
    - **Healthcheck**: `CMD curl -f http://localhost:5003/health`
    - **Ports**: 5003
  - **frontend**
    - **Healthcheck**: *I wasnt able to integrate frontend healthcheck.*
    - **Ports**: 80

---

## 4. Project Documentation

For detailed information on each component, please refer to the following README files:

### 4.1. Backend

- [Data Collector, Data Processor and Notification Service](backend/README.md)

### 4.2. Frontend

- [Frontend With Vue.js](frontend/README.md)

### 4.3. Data Handling

- [MongoDB And RabbitMQ](data/README.md)

### 4.4. Manual and Automatic Data Ingestion

- [Bash](scripts/README.md)

---

## 5. Usage

### 5.1. Prerequisites

- Docker (v20.10+)
- Docker Compose (v2.0+)
- Internet Connection (for packages)

### 5.2. Running the Stack

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


#### Finishing Note

This project challenged me to step out of my comfort zone and explore new technologies.  
Along the way, I gained hands-on experience with microservices architecture, real-time data processing, message queues, and frontend frameworks.  
Overall, it was a rewarding journey that significantly expanded my skill set.
