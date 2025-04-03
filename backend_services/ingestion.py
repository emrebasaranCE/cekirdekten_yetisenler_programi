# ingestion.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
import json
import time
from kafka import KafkaProducer
import uvicorn

app = FastAPI()

# Kafka setup
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Input schema
class PollutionData(BaseModel):
    latitude: float
    longitude: float
    parameter: Literal["PM2.5", "PM10", "NO2", "SO2", "O3"]
    value: float

@app.post("/ingest")
def ingest(data: PollutionData):
    try:
        message = data.dict()
        message["timestamp"] = int(time.time())
        producer.send("raw_pollution_data", value=message)
        return {"status": "Data sent to Kafka successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# This will keep your service alive
if __name__ == "__main__":
    uvicorn.run("ingestion:app", host="0.0.0.0", port=8000, reload=True)
