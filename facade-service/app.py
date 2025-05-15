import os, socket, uuid, random, json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import consul
from kafka import KafkaProducer

app = FastAPI()

CONSUL_HOST = os.getenv("CONSUL_HOST", "consul")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", 8500))
SERVICE_NAME = "facade-service"
SERVICE_ID   = f"{SERVICE_NAME}-{socket.gethostname()}"
SERVICE_PORT = 8000

consul_client = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)
consul_client.agent.service.register(
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
    return {"status": "ok"}

class Message(BaseModel):
    msg: str

_, bs = consul_client.kv.get("config/kafka/bootstrap_servers")
_, tp = consul_client.kv.get("config/kafka/topic")
BOOTSTRAP_SERVERS = bs["Value"].decode().split(",") if bs else ["kafka1:9092","kafka2:9092","kafka3:9092"]
TOPIC             = tp["Value"].decode() if tp else "messages"

def get_instances(service_name: str):
    _, nodes = consul_client.health.service(service_name, passing=True)
    return [(n["Service"]["Address"], n["Service"]["Port"]) for n in nodes]

@app.post("/message")
def post_message(message: Message):
    inst = get_instances("logging-service")
    if not inst:
        raise HTTPException(503, "no logging-service available")
    addr, port = random.choice(inst)
    payload = {"id": str(uuid.uuid4()), "msg": message.msg}
    r = requests.post(f"http://{addr}:{port}/log", json=payload, timeout=3)
    r.raise_for_status()

    producer = KafkaProducer(
      bootstrap_servers=BOOTSTRAP_SERVERS,
      value_serializer=lambda v: json.dumps(v).encode(),
    )
    producer.send(TOPIC, payload)
    producer.flush()

    return payload

# fetch from messages-service + logs, merge by msg
@app.get("/messages")
def get_messages():
    # pick one messages-service
    inst = get_instances("messages-service")
    if not inst:
        raise HTTPException(503, "no messages-service available")
    addr, port = random.choice(inst)
    msgs = requests.get(f"http://{addr}:{port}/messages", timeout=3).json().get("messages", [])

    # pick one logging-service
    inst = get_instances("logging-service")
    addr2, port2 = random.choice(inst)
    logs = requests.get(f"http://{addr2}:{port2}/log", timeout=3).text.splitlines()

    all_msgs = {m["msg"] for m in msgs} | set(logs)
    return {"messages": list(all_msgs)}
