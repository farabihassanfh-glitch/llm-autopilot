import asyncio
import hashlib
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiosqlite

DB_PATH = os.environ.get("DB_PATH", "logs/requests.db")

TIER_MODELS = {
    1: "claude-haiku-4-5-20251001",
    2: "gpt-4o-mini",
    3: "gpt-4o",
}

MODEL_PRICES = {
    "claude-haiku-4-5-20251001": (0.0000008, 0.000004),
    "gpt-4o-mini":               (0.00000015, 0.0000006),
    "gpt-4o":                    (0.000005, 0.000015),
}

TIER_WEIGHTS = [0.55, 0.30, 0.15]  # 55% tier1, 30% tier2, 15% tier3

TIER_TOKEN_RANGES = {
    1: (20, 80,  10, 60),    # input min/max, output min/max
    2: (80, 300, 50, 200),
    3: (150, 600, 100, 400),
}

TIER_LATENCY_RANGES = {
    1: (200, 800),
    2: (400, 1400),
    3: (800, 3000),
}

SAMPLE_HASHES = [
    hashlib.sha256(f"prompt_{i}".encode()).hexdigest()[:16]
    for i in range(500)
]

BATCH_SIZE = 10_000
TOTAL_ROWS = 1_000_000


async def seed(total: int = TOTAL_ROWS):
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
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
        """)
        await db.commit()

        now = datetime.now(timezone.utc)
        inserted = 0

        while inserted < total:
            batch = []
            count = min(BATCH_SIZE, total - inserted)

            for _ in range(count):
                tier = random.choices([1, 2, 3], weights=TIER_WEIGHTS)[0]
                model = TIER_MODELS[tier]
                in_min, in_max, out_min, out_max = TIER_TOKEN_RANGES[tier]
                input_tokens = random.randint(in_min, in_max)
                output_tokens = random.randint(out_min, out_max)
                input_price, output_price = MODEL_PRICES[model]
                cost = input_tokens * input_price + output_tokens * output_price
                lat_min, lat_max = TIER_LATENCY_RANGES[tier]
                latency = random.uniform(lat_min, lat_max)
                age = timedelta(seconds=random.uniform(0, 30 * 24 * 3600))
                ts = (now - age).isoformat()
                prompt_hash = random.choice(SAMPLE_HASHES)
                batch.append((ts, prompt_hash, tier, model, input_tokens, output_tokens, cost, latency))

            await db.executemany(
                "INSERT INTO requests (timestamp, prompt_hash, complexity_tier, model_id, input_tokens, output_tokens, cost_usd, latency_ms) VALUES (?,?,?,?,?,?,?,?)",
                batch,
            )
            await db.commit()
            inserted += count
            print(f"  {inserted:,} / {total:,} rows inserted")

    print(f"\nDone. {total:,} rows in {DB_PATH}")


if __name__ == "__main__":
    asyncio.run(seed())
