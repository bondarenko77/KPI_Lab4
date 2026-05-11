from fastapi import FastAPI, Body
import uvicorn

app = FastAPI()
registry = {}

@app.post("/register")
async def register(data: dict = Body(...)):
    service_name = data.get("service")
    ip_address = data.get("ip")
    if service_name not in registry:
        registry[service_name] = []
    if ip_address not in registry[service_name]:
        registry[service_name].append(ip_address)
    return {"status": "ok"}

@app.get("/lookup/{name}")
async def lookup(name: str):
    return registry.get(name, [])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
