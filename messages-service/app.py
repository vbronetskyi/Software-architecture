import os, socket, threading, time, json
import consul
from fastapi import FastAPI
from kafka import KafkaConsumer

app = FastAPI()
store = []

CONSUL_HOST = os.getenv("CONSUL_HOST", "consul")
CONSUL_PORT = int(os.getenv("CONSUL_PORT", 8500))
SERVICE_NAME = "messages-service"
SERVICE_ID   = f"{SERVICE_NAME}-{socket.gethostname()}"
SERVICE_PORT = 8002

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

_, bs = c.kv.get("config/kafka/bootstrap_servers")
_, tp = c.kv.get("config/kafka/topic")
BOOTSTRAP_SERVERS = bs["Value"].decode().split(",") if bs else ["kafka1:9092","kafka2:9092","kafka3:9092"]
TOPIC             = tp["Value"].decode() if tp else "messages"

def consume_loop():
    while True:
        try:
            consumer = KafkaConsumer(
              TOPIC,
              bootstrap_servers=BOOTSTRAP_SERVERS,
              group_id=f"{SERVICE_NAME}-{socket.gethostname()}",
              auto_offset_reset='earliest',
              value_deserializer=lambda b: json.loads(b.decode())
            )
            for record in consumer:
                store.append(record.value)
                print("Consumed:", record.value)
        except Exception as e:
            print("KafkaConsumer error:", e)
            time.sleep(5)

threading.Thread(target=consume_loop, daemon=True).start()

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/messages")
def get_messages():
    return {"messages": store}
