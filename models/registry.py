from dataclasses import dataclass
from typing import Literal


@dataclass
class ModelConfig:
    model_id: str
    display_name: str
    cost_per_input_token: float
    cost_per_output_token: float
    quality_tier: Literal["low", "medium", "high"]


MODELS: dict[str, ModelConfig] = {
    "gpt-4o": ModelConfig(
        model_id="gpt-4o",
        display_name="GPT-4o",
        cost_per_input_token=0.000005,
        cost_per_output_token=0.000015,
        quality_tier="high",
    ),
    "gpt-4o-mini": ModelConfig(
        model_id="gpt-4o-mini",
        display_name="GPT-4o Mini",
        cost_per_input_token=0.00000015,
        cost_per_output_token=0.0000006,
        quality_tier="medium",
    ),
    "claude-haiku-4-5-20251001": ModelConfig(
        model_id="claude-haiku-4-5-20251001",
        display_name="Claude Haiku 4.5",
        cost_per_input_token=0.0000008,
        cost_per_output_token=0.000004,
        quality_tier="low",
    ),
}
