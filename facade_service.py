import random
import requests
import hazelcast
import uvicorn
import time
from fastapi import FastAPI

app = FastAPI()
CONFIG_SERVER = "http://config-server:8888"

_queue = None

def get_hz_queue():
    global _queue
    if _queue is not None:
        return _queue
    while True:
        try:
            hz = hazelcast.HazelcastClient(
                cluster_members=["hazelcast-node:5701"]
            )
            _queue = hz.get_queue("counter_queue").blocking()
            print("[FACADE] Connected to Hazelcast", flush=True)
            return _queue
        except Exception as e:
            print(f"[FACADE] Hazelcast not ready: {e}, retrying...", flush=True)
            time.sleep(3)

@app.post("/facade")
async def handle_post(msg: str):
    q = get_hz_queue()
    q.put(msg)
    print(f"[FACADE] '{msg}' added to queue", flush=True)
    ips = requests.get(f"{CONFIG_SERVER}/lookup/logging-service", timeout=3).json()
    if ips:
        target = random.choice(ips)
        try:
            requests.post(f"http://{target}/log", json={"msg": msg}, timeout=3)
        except Exception as e:
            print(f"[FACADE] Logging error: {e}", flush=True)
    return {"status": "OK"}

@app.get("/facade")
async def handle_get():
    ips = requests.get(f"{CONFIG_SERVER}/lookup/counter-service", timeout=3).json()
    if ips:
        try:
            return requests.get(f"http://{ips[0]}/value", timeout=3).json()
        except Exception as e:
            print(f"[FACADE] Counter unavailable: {e}", flush=True)
    return {"balance": None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
