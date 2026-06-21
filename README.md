# LLM Cost Autopilot

Automatically routes every prompt to the cheapest model that can handle it — without sacrificing quality.

---

## Results

**73.3% cost reduction** compared to sending every request to Claude Sonnet.

Simple factual questions go to Claude Haiku ($0.000051 per call). Complex reasoning goes to GPT-4o. Everything in between goes to GPT-4o Mini. The savings add up fast.

![Dashboard](https://llm-autopilot-production.up.railway.app/dashboard)

---

## Architecture

```
Request
   │
   ▼
Classifier          ← RandomForest trained on 207 labeled prompts
   │                   extracts: length, word count, sentences,
   │                   presence of complex/simple keywords
   ▼
Router              ← maps predicted tier to the right model
   │
   ▼
LLM API             ← Anthropic or OpenAI depending on tier
   │
   ▼
Response + Logging  ← returns text, model, cost, latency
                       logs every request to SQLite
```

---

## How It Works

The classifier assigns every prompt a complexity tier:

| Tier | Type | Model | Example |
|------|------|-------|---------|
| 1 | Simple facts, translations, reformatting | **Claude Haiku** | "What is the capital of France?" |
| 2 | Summarization, classification, structured analysis | **GPT-4o Mini** | "Summarize this article in 3 bullet points." |
| 3 | Multi-step reasoning, argumentation, nuanced judgment | **GPT-4o** | "Evaluate the trade-offs between REST and GraphQL for a high-read workload." |

The classifier is a `RandomForestClassifier` trained on 207 hand-labeled examples. It runs locally in milliseconds before every API call — no extra network hop.

---

## Live Demo

**https://llm-autopilot-production.up.railway.app/dashboard**

API endpoint:
```bash
curl -X POST https://llm-autopilot-production.up.railway.app/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the capital of France?"}'
```

Response:
```json
{
  "text": "The capital of France is Paris.",
  "model_id": "claude-haiku-4-5-20251001",
  "complexity_tier": 1,
  "cost_usd": 0.0000512,
  "latency_ms": 672.93
}
```

---

## Run It Yourself

```bash
# 1. Clone
git clone https://github.com/farabihassanfh-glitch/llm-autopilot
cd llm-autopilot
git checkout claude/admiring-dijkstra-w5x0ds

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API keys
cp .env.example .env
# edit .env and fill in OPENAI_API_KEY and ANTHROPIC_API_KEY

# 4. Train the classifier
python -m classifier.train

# 5. Start the API
uvicorn api.main:app --reload

# 6. Open the dashboard
open http://localhost:8000/dashboard
```

---

## Tech Stack

- **FastAPI** — REST API and HTML dashboard
- **Anthropic SDK** — Claude Haiku for tier 1 prompts
- **OpenAI SDK** — GPT-4o Mini (tier 2) and GPT-4o (tier 3)
- **scikit-learn** — RandomForestClassifier for prompt complexity detection
- **aiosqlite** — async SQLite for request logging
- **Railway** — cloud deployment
