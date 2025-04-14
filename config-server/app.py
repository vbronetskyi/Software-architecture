from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI()

services = {
    "logging-service": [
        "http://logging-service:8001/log"
    ],
    "messages-service": [
        "http://messages-service:8002/messages"
    ]
}

class ServiceInfo(BaseModel):
    instances: List[str]

@app.get("/services/{service_name}", response_model=ServiceInfo)
def get_service(service_name: str):
    instances = services.get(service_name, [])
    return {"instances": instances}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
