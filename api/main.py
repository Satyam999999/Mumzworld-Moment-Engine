from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.pipeline import MomentEnginePipeline
from src.schemas import MomentBundle
import time, json

app = FastAPI(title="Mumzworld Moment Engine", version="1.0.0",
              description="Life-stage aware notification personalizer for Mumzworld mothers.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

pipeline = MomentEnginePipeline(
    catalog_path="data/catalog.json",
    customers_path="data/customers.json",
    rules_path="data/milestone_rules.json"
)

class NotifyCheckRequest(BaseModel):
    customer_id: str

@app.middleware("http")
async def add_response_time(request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Response-Time"] = f"{(time.time()-start)*1000:.0f}ms"
    return response

@app.post("/notify-check", response_model=MomentBundle)
def notify_check(req: NotifyCheckRequest):
    return pipeline.run(req.customer_id)

@app.get("/health")
def health():
    return {"status": "ok", "service": "mumzworld-moment-engine"}

@app.get("/customers")
def list_customers():
    with open("data/customers.json") as f:
        return [{"customer_id": c["customer_id"], "name": c["name"]}
                for c in json.load(f)]
