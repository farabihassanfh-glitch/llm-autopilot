import requests

API_URL = "https://llm-autopilot-production.up.railway.app/v1/completions"

PROMPTS = [
    # Tier 1 — simple facts, translations, reformatting (34 prompts)
    "What is the capital of Germany?",
    "Translate 'good night' to French.",
    "Convert 72 Fahrenheit to Celsius.",
    "What does CPU stand for?",
    "What is the square root of 256?",
    "How many days are in September?",
    "Translate 'dog' to Spanish.",
    "What is the chemical symbol for silver?",
    "What is 144 divided by 12?",
    "What country uses the currency 'won'?",
    "Convert 10 miles to kilometers.",
    "What does JSON stand for?",
    "What is the largest ocean on Earth?",
    "Translate 'hello' to Greek.",
    "How many meters are in a kilometer?",
    "What is 2 to the power of 8?",
    "What is the boiling point of water in Fahrenheit?",
    "What does IDE stand for in programming?",
    "Translate 'open' to Italian.",
    "What is the atomic number of oxygen?",
    "How many weeks are in a year?",
    "What is the Roman numeral for 50?",
    "What country is the Eiffel Tower in?",
    "Convert 5 kilograms to pounds.",
    "What does DNS stand for?",
    "What is 13 squared?",
    "Translate 'thank you' to Arabic.",
    "How many sides does a pentagon have?",
    "What is the freezing point of water in Celsius?",
    "What does RGB stand for?",
    "What is the currency of India?",
    "How many minutes are in a day?",
    "Translate 'water' to Chinese (pinyin).",
    "What is the smallest continent?",
    # Tier 2 — summarization, classification, structured analysis (33 prompts)
    "Summarize the water cycle in three sentences.",
    "List the pros and cons of electric vehicles.",
    "Classify this sentence as fact or opinion: 'Python is the best programming language.'",
    "Extract the key points from: 'The meeting covered Q3 results, hiring plans, and the new product roadmap.'",
    "What are the main differences between SQL and NoSQL databases?",
    "Summarize what REST APIs are in plain English.",
    "List 5 common causes of software bugs.",
    "Classify this review as positive or negative: 'The product broke after two days and support was unhelpful.'",
    "Summarize the main benefits of cloud computing.",
    "What are the key differences between supervised and unsupervised learning?",
    "List the main components of a neural network.",
    "Summarize what DevOps means in 2-3 sentences.",
    "Identify the tone of: 'We regret to inform you that your application was unsuccessful.'",
    "List the steps in the software development lifecycle.",
    "Summarize the CAP theorem for distributed systems.",
    "What are the differences between HTTP and HTTPS?",
    "List the main types of machine learning algorithms.",
    "Classify this task as frontend or backend: 'Writing a database query to fetch user records.'",
    "Summarize what containerization means in software development.",
    "List the key principles of agile development.",
    "What are the differences between a stack and a queue?",
    "Summarize the role of an API gateway in microservices.",
    "List 5 best practices for writing clean code.",
    "What are the main differences between TCP and UDP?",
    "Summarize what a load balancer does.",
    "Identify the data structure best suited for implementing a browser's back button.",
    "List the main types of software testing.",
    "Summarize what OAuth 2.0 is used for.",
    "What are the differences between authentication and authorization?",
    "List the key components of a CI/CD pipeline.",
    "Summarize the purpose of a message queue in distributed systems.",
    "What are the main differences between monolithic and microservices architectures?",
    "Summarize the key differences between Python 2 and Python 3.",
    # Tier 3 — multi-step reasoning, argumentation, nuanced judgment (33 prompts)
    "A startup has two technical co-founders who disagree on whether to build a mobile app or a web app first. Analyze the trade-offs and recommend a path.",
    "Explain why a system that is highly available is often not strongly consistent, using a concrete example.",
    "A company wants to use AI to screen resumes. Analyze the ethical implications and recommend safeguards.",
    "Should a small team adopt Kubernetes for their first production deployment? Reason through the decision.",
    "Explain how technical debt accumulates and design a strategy for paying it down without halting feature development.",
    "A team is debating whether to use GraphQL or REST for a new API. Walk through the key considerations and give a recommendation.",
    "Analyze why open-source projects often struggle with sustainability despite wide adoption.",
    "A product has 10,000 users and is growing 20% month-over-month. What infrastructure decisions should the team make now vs. later?",
    "Explain how Conway's Law affects software architecture and what teams can do about it.",
    "A developer wants to introduce TypeScript into a large JavaScript codebase. Evaluate the risks and propose a migration strategy.",
    "Should AI-generated code be considered intellectual property? Argue both sides.",
    "A team is choosing between PostgreSQL and MongoDB for a new application. Analyze the trade-offs given the described workload.",
    "Explain the difference between accidental and essential complexity in software, with examples.",
    "A company must decide whether to build or buy a data analytics platform. Walk through the decision framework.",
    "Analyze the risks of a company becoming too dependent on a single cloud provider.",
    "Should engineers be held legally liable for software failures that cause harm? Reason through the ethical and practical dimensions.",
    "A team's test suite takes 45 minutes to run. Analyze the problem and propose solutions without simply 'running fewer tests'.",
    "Explain why distributed systems make debugging harder and what strategies help.",
    "Evaluate whether a recommendation algorithm that maximizes engagement is inherently harmful to users.",
    "A company is considering replacing its senior engineers with AI coding tools. Analyze the long-term consequences.",
    "Should social media platforms be regulated like utilities? Argue both sides.",
    "A team must choose between rewriting a legacy system or incrementally refactoring it. Walk through the decision.",
    "Explain how Goodhart's Law applies to engineering metrics and propose a better measurement approach.",
    "Analyze the trade-offs of moving from a relational database to an event-sourced architecture.",
    "A founder must decide between raising a Series A now or staying bootstrapped for another year. Walk through the reasoning.",
    "Evaluate the argument that 100% test coverage is a harmful goal.",
    "Explain why adding more engineers to a late project often makes it later.",
    "A team is debating remote-first vs. hybrid work. Analyze the impact on engineering culture and productivity.",
    "Should a startup prioritize speed to market or code quality in its first year? Reason through the trade-offs.",
    "Analyze why large language models sometimes produce confident but incorrect answers, and what mitigations exist.",
    "Evaluate the ethical implications of a company training an AI model on its employees' private communications.",
    "A product team has data showing users ignore a key feature. Analyze possible causes and recommend next steps.",
    "Explain the principal-agent problem in the context of software outsourcing and how to mitigate it.",
]


SONNET_INPUT_PRICE = 0.000003
SONNET_OUTPUT_PRICE = 0.000015

MODEL_INPUT_PRICE = {
    "claude-haiku-4-5-20251001": 0.0000008,
    "gpt-4o-mini": 0.00000015,
    "gpt-4o": 0.000005,
}


def estimate_sonnet_cost(model_id: str, actual_cost: float) -> float:
    model_price = MODEL_INPUT_PRICE.get(model_id, SONNET_INPUT_PRICE)
    if model_price == 0:
        return actual_cost
    ratio = SONNET_INPUT_PRICE / model_price
    return actual_cost * ratio


def main():
    print(f"Sending {len(PROMPTS)} prompts to {API_URL}\n")
    print(f"{'#':<5} {'Tier':<5} {'Model':<30} {'Cost':>10} {'Latency':>10}  Prompt")
    print("-" * 110)

    total_cost = 0.0
    total_if_sonnet = 0.0
    tier_counts = {}
    errors = 0

    for i, prompt in enumerate(PROMPTS, 1):
        try:
            resp = requests.post(
                API_URL,
                json={"prompt": prompt},
                timeout=60,
            )
            resp.raise_for_status()
            result = resp.json()

            tier = result.get("complexity_tier", "?")
            model = result["model_id"]
            cost = result["cost_usd"]
            latency = result["latency_ms"]

            sonnet_cost = estimate_sonnet_cost(model, cost)
            total_cost += cost
            total_if_sonnet += sonnet_cost

            if isinstance(tier, int):
                tier_counts[tier] = tier_counts.get(tier, 0) + 1

            short = prompt[:56] + "…" if len(prompt) > 56 else prompt
            print(f"{i:<5} {str(tier):<5} {model:<30} ${cost:>9.6f} {latency:>8.0f}ms  {short}")

        except Exception as e:
            errors += 1
            print(f"{i:<5} ERROR: {e}")

    saved = total_if_sonnet - total_cost
    savings_pct = (saved / total_if_sonnet * 100) if total_if_sonnet > 0 else 0.0

    print("\n" + "=" * 110)
    print("COST SUMMARY")
    print("=" * 110)
    print(f"  Total prompts      : {len(PROMPTS)}  ({errors} errors)")
    print(f"  Tier distribution  : Tier 1={tier_counts.get(1,0)}  Tier 2={tier_counts.get(2,0)}  Tier 3={tier_counts.get(3,0)}")
    print(f"  Actual cost        : ${total_cost:.6f}")
    print(f"  Cost if all Sonnet : ${total_if_sonnet:.6f}")
    print(f"  Total saved        : ${saved:.6f}  ({savings_pct:.1f}% cheaper)")


if __name__ == "__main__":
    main()
