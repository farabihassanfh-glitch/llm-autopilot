import asyncio
from pathlib import Path

from classifier.classifier import load_model, predict
from models.client import send_request
from models.registry import MODELS
from models.response import LLMResponse

_MODEL_PATH = Path(__file__).parent.parent / "classifier" / "model.joblib"

_TIER_MAP = {
    1: "claude-haiku-4-5-20251001",
    2: "gpt-4o-mini",
    3: "gpt-4o",
}


async def route(prompt: str) -> LLMResponse:
    model = load_model(str(_MODEL_PATH))
    tier = predict(prompt, model)
    model_id = _TIER_MAP[tier]
    model_config = MODELS[model_id]
    response = await send_request(prompt, model_config)
    response.complexity_tier = tier
    return response
