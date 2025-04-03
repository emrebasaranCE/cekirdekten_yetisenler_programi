# processing_service/main.py
import json
from kafka import KafkaConsumer
from pymongo import MongoClient

# Kafka setup
consumer = KafkaConsumer(
    'raw_pollution_data',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='pollution-processing-group'
)

# MongoDB setup
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["pollution"]
collection = db["pollution_data"]

print("[PROCESSING SERVICE] Listening to Kafka...")

for message in consumer:
    data = message.value
    print(f"[NEW DATA] {data}")
    collection.insert_one(data)
