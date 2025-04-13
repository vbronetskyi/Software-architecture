from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import requests
import random
import uvicorn

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

class Message(BaseModel):
    msg: str

@app.post("/message")
def post_message(message: Message):
    msg_id = str(uuid.uuid4())
    payload = {"id": msg_id, "msg": message.msg}

    retries = 3
    success = False
    for attempt in range(retries):
        logging_service_url = get_service_url("logging-service", "http://logging-service:8001/log")
        try:
            response = requests.post(logging_service_url, json=payload, timeout=2)
            response.raise_for_status()
            print(f"Attempt {attempt+1}: Successfully sent message {msg_id} to {logging_service_url}")
            success = True
            break
        except Exception as e:
            print(f"Attempt {attempt+1}: Failed to send message {msg_id} to {logging_service_url}. Error: {e}")
            continue

    if not success:
        raise HTTPException(status_code=500, detail="logging-service unavailable")

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
        static_message = msg_response.text
    except Exception as e:
        static_message = f"messages-service unavailable: {e}"

    return {"result": log_messages + "\n" + static_message}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
