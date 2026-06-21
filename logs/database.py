import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from models.response import LLMResponse

# Use /data volume on Railway, fall back to logs/ locally
_data_dir = Path("/data") if Path("/data").exists() else Path("logs")
_data_dir.mkdir(parents=True, exist_ok=True)
DB_PATH = str(_data_dir / "requests.db")

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS requests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT    NOT NULL,
    prompt_hash     TEXT    NOT NULL,
    complexity_tier INTEGER,
    model_id        TEXT    NOT NULL,
    input_tokens    INTEGER NOT NULL,
    output_tokens   INTEGER NOT NULL,
    cost_usd        REAL    NOT NULL,
    latency_ms      REAL    NOT NULL
)
"""


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(_CREATE_TABLE)
        await db.commit()


async def log_request(prompt: str, response: LLMResponse) -> None:
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
    timestamp = datetime.now(timezone.utc).isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO requests
                (timestamp, prompt_hash, complexity_tier, model_id,
                 input_tokens, output_tokens, cost_usd, latency_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp,
                prompt_hash,
                response.complexity_tier,
                response.model_id,
                response.input_tokens,
                response.output_tokens,
                response.cost_usd,
                response.latency_ms,
            ),
        )
        await db.commit()
