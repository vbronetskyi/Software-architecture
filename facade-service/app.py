from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import time
import requests
from grpc_client import send_log_message

app = FastAPI()

class Message(BaseModel):
    msg: str

@app.post("/message")
def post_message(message: Message):
    msg_id = str(uuid.uuid4())
    payload_msg = message.msg

    retries = 3
    for attempt in range(retries):
        try:
            status = send_log_message(msg_id, payload_msg)
            print(f"Attempt {attempt+1}: gRPC call status: {status}")
            if status in ("saved", "duplicate"):
                break
            else:
                raise Exception("Unexpected status returned")
        except Exception as e:
            print(f"Attempt {attempt+1}: Failed gRPC call for message id {msg_id}. Error: {e}")
            time.sleep(1)  # small delay before retrying
            if attempt == retries - 1:
                raise HTTPException(status_code=500, detail="logging-service gRPC unavailable")

    return {"id": msg_id, "msg": payload_msg}

@app.get("/messages")
def get_messages():
    try:
        log_response = requests.get("http://logging-service:8001/log", timeout=2)
        log_response.raise_for_status()
        log_messages = log_response.text
    except Exception as e:
        print(f"Failed to fetch messages from logging-service: {e}")
        log_messages = "logging-service unavailable"
    
    try:
        msg_response = requests.get("http://messages-service:8002/messages", timeout=2)
        msg_response.raise_for_status()
        static_message = msg_response.text
    except Exception as e:
        print(f"Failed to fetch messages from messages-service: {e}")
        static_message = "messages-service unavailable"
    
    return {"result": log_messages + "\n" + static_message}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
