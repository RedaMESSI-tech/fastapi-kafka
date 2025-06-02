from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import os

app = FastAPI()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC_NAME = os.getenv("TOPIC_NAME", "auth-events")

producer = None  # On initialise à None pour éviter un crash au démarrage

def get_producer():
    global producer
    if producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception as e:
            print(f"[Kafka ERROR] Impossible de créer le producteur : {e}")
            return None
    return producer

class Message(BaseModel):
    user_id: int
    event: str

@app.get("/ping")
def ping():
    return {"message": "API OK"}

@app.post("/publish")
def publish(msg: Message):
    try:
        prod = get_producer()
        if not prod:
            return {"error": "Kafka broker non disponible"}
        prod.send(TOPIC_NAME, msg.dict())
        prod.flush()
        return {"status": "sent", "message": msg.dict()}
    except Exception as e:
        return {"error": str(e)}
