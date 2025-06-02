from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import os

app = FastAPI()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = os.getenv("TOPIC_NAME", "auth-events")

# Init Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

class Message(BaseModel):
    user_id: int
    event: str

@app.get("/ping")
def ping():
    return {"message": "API OK"}

@app.post("/publish")
def publish(msg: Message):
    try:
        producer.send(TOPIC_NAME, msg.dict())
        producer.flush()
        return {"status": "sent", "message": msg.dict()}
    except Exception as e:
        return {"error": str(e)}
