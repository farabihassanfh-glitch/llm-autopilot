from fastapi import FastAPI
from pydantic import BaseModel

from router.router import route

app = FastAPI()


class CompletionRequest(BaseModel):
    prompt: str


class CompletionResponse(BaseModel):
    text: str
    model_id: str
    complexity_tier: int | None
    cost_usd: float
    latency_ms: float


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/v1/completions", response_model=CompletionResponse)
async def completions(request: CompletionRequest):
    result = await route(request.prompt)
    return CompletionResponse(
        text=result.text,
        model_id=result.model_id,
        complexity_tier=result.complexity_tier,
        cost_usd=result.cost_usd,
        latency_ms=result.latency_ms,
    )
