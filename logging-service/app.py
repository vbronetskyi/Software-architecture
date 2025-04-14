from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import hazelcast

app = FastAPI()

hz_client = hazelcast.HazelcastClient(
    cluster_members=["hazelcast-server1:5701", "hazelcast-server2:5701"]
)
dist_map = hz_client.get_map("messages").blocking()

class LogMessage(BaseModel):
    id: str
    msg: str

@app.post("/log")
def log_message(message: LogMessage):
    if dist_map.contains_key(message.id):
        return {"status": "duplicate"}
    dist_map.put(message.id, message.msg)
    print(f"Received message: {message.id} -> {message.msg}")
    return {"status": "saved"}

@app.get("/log")
def get_all_messages():
    entries = dist_map.entry_set()
    all_messages = "\n".join(msg for (_, msg) in entries)
    return all_messages

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
