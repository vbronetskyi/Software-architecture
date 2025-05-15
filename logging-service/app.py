import os, socket
import consul
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
store = []

CONSUL_HOST = os.getenv("CONSUL_HOST", "consul")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", 8500))
SERVICE_NAME = "logging-service"
SERVICE_ID   = f"{SERVICE_NAME}-{socket.gethostname()}"
SERVICE_PORT = 8001

c = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)
c.agent.service.register(
    name=SERVICE_NAME,
    service_id=SERVICE_ID,
    address=SERVICE_NAME,
    port=SERVICE_PORT,
    check={
      "http":     f"http://{SERVICE_NAME}:{SERVICE_PORT}/health",
      "interval": "10s",
      "timeout":  "1s"
    }
)

@app.get("/health")
def health():
    return {"status":"ok"}

class LogMessage(BaseModel):
    id: str
    msg: str

@app.post("/log")
def log(msg: LogMessage):
    if msg.id not in {m["id"] for m in store}:
        store.append({"id": msg.id, "msg": msg.msg})
        print(f"Logged: {msg.id} -> {msg.msg}")
    return {"status": "saved"}

@app.get("/log")
def get_log():
    return "\n".join(m["msg"] for m in store)
