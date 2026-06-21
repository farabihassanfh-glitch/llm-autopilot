from contextlib import asynccontextmanager

import aiosqlite
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from logs.database import DB_PATH, init_db, log_request
from router.router import route

SONNET_PRICE_INPUT = 0.000003
SONNET_PRICE_OUTPUT = 0.000015


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


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
    await log_request(request.prompt, result)
    return CompletionResponse(
        text=result.text,
        model_id=result.model_id,
        complexity_tier=result.complexity_tier,
        cost_usd=result.cost_usd,
        latency_ms=result.latency_ms,
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM requests ORDER BY timestamp DESC"
        ) as cur:
            rows = await cur.fetchall()

    total_requests = len(rows)
    total_cost = sum(r["cost_usd"] for r in rows)
    total_if_sonnet = sum(
        r["input_tokens"] * SONNET_PRICE_INPUT + r["output_tokens"] * SONNET_PRICE_OUTPUT
        for r in rows
    )
    total_saved = total_if_sonnet - total_cost
    savings_pct = (total_saved / total_if_sonnet * 100) if total_if_sonnet > 0 else 0.0

    rows_html = "\n".join(
        f"""<tr>
              <td>{r['timestamp'][:19]}</td>
              <td><code>{r['prompt_hash']}</code></td>
              <td>{r['complexity_tier']}</td>
              <td>{r['model_id']}</td>
              <td>{r['input_tokens']}</td>
              <td>{r['output_tokens']}</td>
              <td>${r['cost_usd']:.6f}</td>
              <td>{r['latency_ms']:.0f} ms</td>
            </tr>"""
        for r in rows
    )

    no_data_row = (
        '<tr><td colspan="8" style="text-align:center;color:#888">No requests yet</td></tr>'
        if not rows
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LLM Autopilot Dashboard</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: system-ui, sans-serif; background: #f5f7fa; color: #1a1a2e; padding: 2rem; }}
    h1 {{ font-size: 1.8rem; margin-bottom: 1.5rem; }}
    h2 {{ font-size: 1.1rem; margin-bottom: 1rem; color: #444; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
    .card {{ background: #fff; border-radius: 10px; padding: 1.2rem 1.5rem; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
    .card .label {{ font-size: .8rem; color: #888; text-transform: uppercase; letter-spacing: .05em; margin-bottom: .3rem; }}
    .card .value {{ font-size: 1.6rem; font-weight: 700; color: #1a1a2e; }}
    .card .sub {{ font-size: .85rem; color: #22c55e; margin-top: .2rem; font-weight: 600; }}
    .section {{ background: #fff; border-radius: 10px; padding: 1.5rem; box-shadow: 0 1px 4px rgba(0,0,0,.08); margin-bottom: 2rem; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .85rem; }}
    th {{ text-align: left; padding: .6rem .8rem; border-bottom: 2px solid #e5e7eb; color: #555; font-weight: 600; white-space: nowrap; }}
    td {{ padding: .55rem .8rem; border-bottom: 1px solid #f0f0f0; white-space: nowrap; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #fafafa; }}
    code {{ background: #f3f4f6; padding: .1em .35em; border-radius: 4px; font-size: .8rem; }}
  </style>
</head>
<body>
  <h1>LLM Autopilot Dashboard</h1>

  <div class="metrics">
    <div class="card">
      <div class="label">Total Requests</div>
      <div class="value">{total_requests}</div>
    </div>
    <div class="card">
      <div class="label">Total Actual Cost</div>
      <div class="value">${total_cost:.4f}</div>
    </div>
    <div class="card">
      <div class="label">Cost if All Sonnet</div>
      <div class="value">${total_if_sonnet:.4f}</div>
    </div>
    <div class="card">
      <div class="label">Total Saved</div>
      <div class="value">${total_saved:.4f}</div>
      <div class="sub">↓ {savings_pct:.1f}% cheaper</div>
    </div>
  </div>

  <div class="section">
    <h2>Recent Requests</h2>
    <table>
      <thead>
        <tr>
          <th>Timestamp</th>
          <th>Prompt Hash</th>
          <th>Tier</th>
          <th>Model</th>
          <th>Input Tokens</th>
          <th>Output Tokens</th>
          <th>Cost</th>
          <th>Latency</th>
        </tr>
      </thead>
      <tbody>
        {rows_html or no_data_row}
      </tbody>
    </table>
  </div>
</body>
</html>"""
