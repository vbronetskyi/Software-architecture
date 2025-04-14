import os
import socket
import time
import json
import threading
from fastapi import FastAPI
import uvicorn
from kafka import KafkaConsumer

app = FastAPI()

consumed_messages = []

unique_group_id = os.getenv("CONSUMER_GROUP") or f"messages-service-{socket.gethostname()}"
print(f"Using consumer group: {unique_group_id}")

def consume_messages():
    time.sleep(20)
    max_attempts = 5
    consumer = None
    for attempt in range(max_attempts):
        try:
            consumer = KafkaConsumer(
                'messages',
                bootstrap_servers=["kafka1:9092", "kafka2:9092", "kafka3:9092"],
                auto_offset_reset='earliest',
                group_id=unique_group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            print("Successfully connected to Kafka brokers")
            break
        except Exception as e:
            print(f"Attempt {attempt+1}: Failed to create KafkaConsumer: {e}")
            time.sleep(5)
    if consumer is None:
        print("Exiting: Could not connect to Kafka brokers")
        return
    for message in consumer:
        print(f"Consumed message: {message.value}")
        consumed_messages.append(message.value)

consumer_thread = threading.Thread(target=consume_messages, daemon=True)
consumer_thread.start()

@app.get("/messages")
def get_messages():
    return {"messages": consumed_messages}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
