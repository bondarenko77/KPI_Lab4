import hazelcast, requests, threading, uvicorn, socket
from fastapi import FastAPI

app = FastAPI()
balance = 0
hz = hazelcast.HazelcastClient(cluster_members=["hazelcast-node:5701"])
queue = hz.get_queue("counter_queue").blocking()

def worker():
    global balance
    while True:
        msg = queue.take()
        balance += 1

threading.Thread(target=worker, daemon=True).start()

@app.get("/value")
async def get_val():
    return {"balance": balance}

@app.on_event("startup")
def register():
    ip = f"{socket.gethostbyname(socket.gethostname())}:8002"
    requests.post("http://config-server:8888/register", json={"service": "counter-service", "ip": ip})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
