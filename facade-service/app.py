from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import requests
import random
import uvicorn
import json
from kafka import KafkaProducer

app = FastAPI()

CONFIG_SERVER_URL = "http://config-server:8003"

def get_service_url(service_name: str, default_url: str) -> str:
    try:
        response = requests.get(f"{CONFIG_SERVER_URL}/services/{service_name}", timeout=2)
        response.raise_for_status()
        data = response.json()
        instances = data.get("instances", [])
        if instances:
            return random.choice(instances)
        else:
            return default_url
    except Exception as e:
        print(f"Error retrieving config for {service_name}: {e}")
        return default_url

producer = KafkaProducer(
    bootstrap_servers=["kafka1:9092", "kafka2:9092", "kafka3:9092"],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

class Message(BaseModel):
    msg: str

@app.post("/message")
def post_message(message: Message):
    msg_id = str(uuid.uuid4())
    payload = {"id": msg_id, "msg": message.msg}
    
    # send to logging-service
    retries = 3
    success_log = False
    for attempt in range(retries):
        logging_service_url = get_service_url("logging-service", "http://logging-service:8001/log")
        try:
            response = requests.post(logging_service_url, json=payload, timeout=2)
            response.raise_for_status()
            print(f"Attempt {attempt+1}: Successfully sent message {msg_id} to {logging_service_url}")
            success_log = True
            break
        except Exception as e:
            print(f"Attempt {attempt+1}: Failed to send message {msg_id} to {logging_service_url}. Error: {e}")
            continue
    if not success_log:
        raise HTTPException(status_code=500, detail="logging-service unavailable")
    
    try:
        producer.send("messages", payload)
        producer.flush()
        print(f"Message {msg_id} sent to Kafka topic 'messages'")
    except Exception as e:
        print(f"Failed to send message {msg_id} to Kafka. Error: {e}")
        raise HTTPException(status_code=500, detail="Kafka error")
    
    return {"id": msg_id, "msg": message.msg}

@app.get("/messages")
def get_messages():
    try:
        logging_service_url = get_service_url("logging-service", "http://logging-service:8001/log")
        log_response = requests.get(logging_service_url, timeout=2)
        log_response.raise_for_status()
        log_messages = log_response.text
    except Exception as e:
        log_messages = f"logging-service unavailable: {e}"
    
    try:
        messages_service_url = get_service_url("messages-service", "http://messages-service:8002/messages")
        msg_response = requests.get(messages_service_url, timeout=2)
        msg_response.raise_for_status()
        service_messages = msg_response.text
    except Exception as e:
        service_messages = f"messages-service unavailable: {e}"
    
    combined = log_messages + "\n" + service_messages
    return {"result": combined}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
