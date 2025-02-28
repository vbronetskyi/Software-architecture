from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# key = UUID, value = message text
messages = {}

class LogMessage(BaseModel):
    id: str
    msg: str

@app.post("/log")
def log_message(message: LogMessage):
    if message.id in messages:
        return {"status": "duplicate"}
    messages[message.id] = message.msg
    print(f"Received message: {message.id} -> {message.msg}")
    return {"status": "saved"}

@app.get("/log")
def get_all_messages():
    return "\n".join(messages.values())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
