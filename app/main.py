from fastapi import FastAPI
from temporalio.client import Client
from app.workflows import HelloWorkflow

app = FastAPI()
temporal_client = None

@app.on_event("startup")
async def startup():
    global temporal_client
    temporal_client = await Client.connect("temporal:7233")

@app.post("/run-workflow")
async def run_workflow(name: str):
    result = await temporal_client.start_workflow(
        HelloWorkflow.run,
        name,
        id=f"hello-{name}",
        task_queue="default",
    )
    return {"workflow_id": result.id}
