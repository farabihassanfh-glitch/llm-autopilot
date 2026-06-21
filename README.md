# LLM Cost Autopilot

Automatically routes every prompt to the cheapest model that can handle it — without sacrificing quality.

---

## Results

**73.3% cost reduction** compared to sending every request to Claude Sonnet.

Simple factual questions go to Claude Haiku. Complex reasoning goes to GPT-4o. Everything in between goes to GPT-4o Mini. The savings add up fast.

---

## Architecture

```
Request
   │
   ▼
Classifier          ← RandomForestClassifier trained on 207 labeled prompts
   │                   features: length, word count, sentence count,
   │                   complex/medium/simple keyword signals
   ▼
Router              ← maps predicted tier to the cheapest capable model
   │
   ▼
LLM API             ← Anthropic (Haiku) or OpenAI (GPT-4o Mini / GPT-4o)
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
| 1 | Simple facts, translations, reformatting | **Claude Haiku 4.5** | "What is the capital of France?" |
| 2 | Summarization, classification, structured analysis | **GPT-4o Mini** | "Summarize the pros and cons of remote work." |
| 3 | Multi-step reasoning, argumentation, nuanced judgment | **GPT-4o** | "Analyze the ethical trade-offs of AI in criminal sentencing and argue for a policy recommendation." |

The classifier is a `RandomForestClassifier` trained on 207 hand-labeled examples. It runs in milliseconds before every API call — no extra network hop, no added latency.

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
  "latency_ms": 1013.3
}
```

---

## Run It Yourself

```bash
# 1. Clone
git clone https://github.com/farabihassanfh-glitch/llm-autopilot
cd llm-autopilot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API keys
export ANTHROPIC_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here

# 4. Train the classifier
python -m classifier.train

# 5. Start the API
uvicorn api.main:app --reload

# 6. Open the dashboard
open http://localhost:8000/dashboard
```

---

## Tech Stack

- **FastAPI** — async REST API and live HTML dashboard
- **scikit-learn** — RandomForestClassifier for prompt complexity detection
- **Anthropic SDK** — Claude Haiku 4.5 for tier 1 prompts
- **OpenAI SDK** — GPT-4o Mini (tier 2) and GPT-4o (tier 3)
- **aiosqlite** — async SQLite for request logging
- **Railway** — cloud deployment with nixpacks
