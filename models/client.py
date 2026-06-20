import os
import time

import anthropic
import openai

from models.registry import ModelConfig
from models.response import LLMResponse


def _openai_client() -> openai.AsyncOpenAI:
    return openai.AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])


def _anthropic_client() -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


async def send_request(prompt: str, model_config: ModelConfig) -> LLMResponse:
    start = time.monotonic()

    if model_config.model_id.startswith("gpt-"):
        client = _openai_client()
        response = await client.chat.completions.create(
            model=model_config.model_id,
            messages=[{"role": "user", "content": prompt}],
        )
        latency_ms = (time.monotonic() - start) * 1000
        text = response.choices[0].message.content or ""
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

    elif model_config.model_id.startswith("claude-"):
        client = _anthropic_client()
        response = await client.messages.create(
            model=model_config.model_id,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        latency_ms = (time.monotonic() - start) * 1000
        text = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

    else:
        raise ValueError(f"Unknown provider for model: {model_config.model_id}")

    return LLMResponse(
        text=text,
        model_id=model_config.model_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=model_config.estimate_cost(input_tokens, output_tokens),
        latency_ms=latency_ms,
    )
