from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/messages")
def get_message():
    return "This is the messages-service static message."

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
