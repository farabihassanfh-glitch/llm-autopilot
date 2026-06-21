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
@app.get("/savings", response_class=HTMLResponse)
async def savings_dashboard():
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

    tier_counts = {{1: 0, 2: 0, 3: 0}}
    model_counts = {{}}
    for r in rows:
        t = r["complexity_tier"]
        if t in tier_counts:
            tier_counts[t] += 1
        m = r["model_id"]
        model_counts[m] = model_counts.get(m, 0) + 1

    tier_bar = ""
    if total_requests:
        for tier, label, color in [
            (1, "Tier 1 · Haiku", "#6366f1"),
            (2, "Tier 2 · GPT-4o Mini", "#f59e0b"),
            (3, "Tier 3 · GPT-4o", "#ef4444"),
        ]:
            pct = tier_counts[tier] / total_requests * 100
            tier_bar += f'<div style="display:flex;align-items:center;gap:.75rem;margin-bottom:.5rem"><span style="width:140px;font-size:.8rem;color:#555">{label}</span><div style="flex:1;background:#f3f4f6;border-radius:99px;height:10px"><div style="width:{pct:.1f}%;background:{color};height:10px;border-radius:99px"></div></div><span style="font-size:.8rem;color:#888;width:40px;text-align:right">{tier_counts[tier]}</span></div>'

    rows_html = "\n".join(
        f"""<tr>
              <td>{r['timestamp'][:19].replace('T',' ')}</td>
              <td><code>{r['prompt_hash']}</code></td>
              <td><span class="badge tier{r['complexity_tier']}">Tier {r['complexity_tier']}</span></td>
              <td style="font-size:.8rem">{r['model_id']}</td>
              <td style="text-align:right">{r['input_tokens']}</td>
              <td style="text-align:right">{r['output_tokens']}</td>
              <td style="text-align:right">${r['cost_usd']:.6f}</td>
              <td style="text-align:right">{r['latency_ms']:.0f} ms</td>
            </tr>"""
        for r in rows[:200]
    )

    no_data_row = (
        '<tr><td colspan="8" style="text-align:center;padding:2rem;color:#aaa">No requests yet — send one to <code>/v1/completions</code></td></tr>'
        if not rows else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LLM Cost Savings — Autopilot</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: system-ui, -apple-system, sans-serif; background: #0f1117; color: #e2e8f0; min-height: 100vh; }}
    .topbar {{ background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); padding: 2rem 2.5rem 1.5rem; border-bottom: 1px solid #2d2d4e; }}
    .topbar h1 {{ font-size: 1.6rem; font-weight: 800; letter-spacing: -.02em; color: #fff; }}
    .topbar p {{ font-size: .9rem; color: #a5b4fc; margin-top: .3rem; }}
    .content {{ padding: 2rem 2.5rem; max-width: 1400px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
    .card {{ background: #1a1d27; border: 1px solid #2d2d4e; border-radius: 12px; padding: 1.4rem 1.6rem; }}
    .card .label {{ font-size: .72rem; color: #6b7280; text-transform: uppercase; letter-spacing: .08em; margin-bottom: .4rem; }}
    .card .value {{ font-size: 1.9rem; font-weight: 800; color: #f1f5f9; line-height: 1; }}
    .card .sub {{ font-size: .82rem; margin-top: .4rem; font-weight: 600; }}
    .green {{ color: #4ade80; }}
    .muted {{ color: #94a3b8; }}
    .section {{ background: #1a1d27; border: 1px solid #2d2d4e; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }}
    .section-title {{ font-size: .8rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: #6b7280; margin-bottom: 1.2rem; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .82rem; }}
    th {{ text-align: left; padding: .5rem .75rem; border-bottom: 1px solid #2d2d4e; color: #6b7280; font-weight: 600; white-space: nowrap; }}
    th:not(:first-child):not(:nth-child(2)):not(:nth-child(3)):not(:nth-child(4)) {{ text-align: right; }}
    td {{ padding: .5rem .75rem; border-bottom: 1px solid #1e2133; white-space: nowrap; color: #cbd5e1; }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #1e2133; }}
    code {{ background: #0f1117; border: 1px solid #2d2d4e; padding: .1em .4em; border-radius: 4px; font-size: .78rem; color: #a5b4fc; }}
    .badge {{ display: inline-block; padding: .15em .55em; border-radius: 99px; font-size: .72rem; font-weight: 700; }}
    .badge.tier1 {{ background: #1e1b4b; color: #818cf8; }}
    .badge.tier2 {{ background: #2d1d00; color: #fbbf24; }}
    .badge.tier3 {{ background: #2d0f0f; color: #f87171; }}
    .savings-hero {{ text-align: center; padding: .5rem 0 1rem; }}
    .savings-hero .big {{ font-size: 3.5rem; font-weight: 900; color: #4ade80; line-height: 1; }}
    .savings-hero .desc {{ font-size: .9rem; color: #6b7280; margin-top: .4rem; }}
  </style>
</head>
<body>
  <div class="topbar">
    <h1>💸 LLM Cost Savings</h1>
    <p>Every prompt is auto-routed to the cheapest model that can handle it — no quality trade-off.</p>
  </div>
  <div class="content">

    <div class="metrics">
      <div class="card">
        <div class="label">Total Requests</div>
        <div class="value">{total_requests:,}</div>
        <div class="sub muted">all time</div>
      </div>
      <div class="card">
        <div class="label">Actual Cost</div>
        <div class="value">${total_cost:.4f}</div>
        <div class="sub muted">with smart routing</div>
      </div>
      <div class="card">
        <div class="label">Without Autopilot</div>
        <div class="value">${total_if_sonnet:.4f}</div>
        <div class="sub muted">if all sent to Sonnet</div>
      </div>
      <div class="card" style="border-color:#166534">
        <div class="label">Money Saved</div>
        <div class="value" style="color:#4ade80">${total_saved:.4f}</div>
        <div class="sub green">↓ {savings_pct:.1f}% cheaper</div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">Requests by complexity tier</div>
      {tier_bar or '<p style="color:#6b7280;font-size:.85rem">No data yet.</p>'}
    </div>

    <div class="section">
      <div class="section-title">Recent requests (last 200)</div>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Prompt</th>
            <th>Tier</th>
            <th>Model</th>
            <th>In</th>
            <th>Out</th>
            <th>Cost</th>
            <th>Latency</th>
          </tr>
        </thead>
        <tbody>
          {rows_html or no_data_row}
        </tbody>
      </table>
    </div>

  </div>
</body>
</html>"""
