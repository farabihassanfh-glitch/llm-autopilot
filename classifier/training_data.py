EXAMPLES: list[dict] = [
    # Tier 1: simple facts, translations, reformatting
    {"prompt": "What is the capital of France?", "tier": 1},
    {"prompt": "Translate 'good morning' to Spanish.", "tier": 1},
    {"prompt": "Convert 100 Fahrenheit to Celsius.", "tier": 1},
    {"prompt": "What does HTTP stand for?", "tier": 1},
    {"prompt": "Reformat this date: 06/20/2026 → June 20, 2026.", "tier": 1},
    {"prompt": "What is the plural of 'octopus'?", "tier": 1},
    {"prompt": "Translate 'thank you' to Japanese.", "tier": 1},
    {"prompt": "How many days are in a leap year?", "tier": 1},
    {"prompt": "What is 17 multiplied by 8?", "tier": 1},
    {"prompt": "Convert this JSON to YAML: {\"name\": \"Alice\", \"age\": 30}.", "tier": 1},

    # Tier 2: summarization, classification, structured analysis
    {"prompt": "Summarize the following news article in three bullet points.", "tier": 2},
    {"prompt": "Classify this customer review as positive, negative, or neutral.", "tier": 2},
    {"prompt": "Extract all action items from this meeting transcript.", "tier": 2},
    {"prompt": "Summarize the key differences between REST and GraphQL.", "tier": 2},
    {"prompt": "Given this resume, list the candidate's top five technical skills.", "tier": 2},
    {"prompt": "Categorize these 20 support tickets by issue type.", "tier": 2},
    {"prompt": "Summarize this research paper's methodology and findings.", "tier": 2},
    {"prompt": "Identify the sentiment trend across these five product reviews.", "tier": 2},
    {"prompt": "List the pros and cons of remote work based on this article.", "tier": 2},
    {"prompt": "Parse this job description and output required vs. preferred qualifications.", "tier": 2},

    # Tier 3: multi-step reasoning, argumentation, nuanced judgment
    {"prompt": "A company is deciding whether to rewrite its monolith in microservices. Analyze the trade-offs and recommend a strategy.", "tier": 3},
    {"prompt": "Given conflicting evidence in two studies, evaluate which conclusion is better supported and why.", "tier": 3},
    {"prompt": "A user's pull request improves performance but reduces readability. Should it be merged? Justify your decision.", "tier": 3},
    {"prompt": "Construct a counter-argument to the claim that AI will eliminate more jobs than it creates.", "tier": 3},
    {"prompt": "A startup has $50k runway and two possible pivots. Which should they pursue? Walk through the reasoning.", "tier": 3},
    {"prompt": "Explain why a sorting algorithm that is O(n log n) on average might still be slower than O(n²) in practice.", "tier": 3},
    {"prompt": "Evaluate the ethical implications of training a content moderation model on biased historical data.", "tier": 3},
    {"prompt": "A patient presents with three overlapping symptoms. What differential diagnoses should be considered and how would you triage?", "tier": 3},
    {"prompt": "Critique this policy proposal for universal basic income, addressing both its economic and social dimensions.", "tier": 3},
    {"prompt": "Two engineers disagree on database normalization vs. denormalization for a high-read workload. Mediate the debate with a recommendation.", "tier": 3},
]
