import requests, socket, uvicorn, os
from fastapi import FastAPI, Body

app = FastAPI()
CONFIG_SERVER = "http://config-server:8888"

@app.post("/log")
async def log_msg(data: dict = Body(...)):
    print(f"LOG: {data.get('msg')}")
    return {"status": "done"}

@app.on_event("startup")
def register():
    ip = f"{socket.gethostbyname(socket.gethostname())}:8001"
    requests.post(f"{CONFIG_SERVER}/register", json={"service": "logging-service", "ip": ip})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
