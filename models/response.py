from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    model_id: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
