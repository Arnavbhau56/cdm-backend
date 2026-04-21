# OpenAI service: uploads PDF to Files API, calls gpt-4o with structured VC analysis prompt,
# returns parsed JSON with startup_name, sector, founder_email, business_model, industry_context, key_risks, founder_questions.

import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

SYSTEM_PROMPT = """You are a senior venture capital analyst working for CDM Capital, an early-stage VC firm.

Firm context:
- Sectors we focus on: {sectors_focus}
- Stage we focus on: {stage_focus}
- Our question style: {question_style}
- Additional context: {additional_context}

A startup pitch deck has been attached as a file.

Your task is NOT to summarize slides superficially. Your task is to think like an investor preparing for a first founder meeting and produce deep, commercially useful analysis.

You must reason carefully about:
- What the company is actually selling vs how it is marketed.
- Whether the problem is painful enough to create real demand.
- How the product compares with existing incumbents, startups, in-house solutions, and substitutes.
- Whether the claimed differentiation is structural, temporary, or weak.
- How this market typically behaves and what determines winners.
- What assumptions must be true for this company to become venture-scale.
- Hidden risks, missing information, inconsistencies, or overclaims in the deck.
- What sophisticated investors would immediately want clarified.

Do not accept deck claims at face value. Infer thoughtfully from what is shown and what is omitted.

Return ONLY a valid JSON object with exactly these 7 keys. No markdown. No explanation outside the JSON."""

USER_PROMPT = """Analyze the attached pitch deck and return this exact JSON structure:

{
  "startup_name": "The exact name of the startup as it appears in the deck.",

  "sector": "2-3 relevant sector labels, comma-separated (e.g. Fintech, SaaS or Healthtech, B2B, Deeptech).",

  "founder_email": "Email address of the founder or company contact if present in the deck. If not found, return empty string.",

  "business_model": "Write a sharp investor-grade explanation of what the company does, who pays them, how revenue is generated, what customer workflow they fit into, why customers would switch from current alternatives, and what must happen for revenue to scale materially. Avoid generic wording.",

  "industry_context": "Provide a deep explanation of how this category usually works. Include buying behavior, sales cycles, margins, competition structure, switching costs, regulatory or operational constraints, common failure modes, growth levers, and notable comparable companies or venture-backed precedents where relevant. Explain what separates winners from average players.",

  "key_risks": [
    "Risk 1 — Explain the precise mechanism of risk. Reference specific claims, omissions, metrics, GTM assumptions, competition, unit economics, legal structure, founder dependency, or unclear evidence from the deck.",
    "Risk 2...",
    "Risk 3...",
    "Risk 4...",
    "Risk 5..."
  ],

  "founder_questions": [
    {"question": "Question 1 — highest priority legal / structural / ownership / compliance issue based on the deck", "answer": ""},
    {"question": "Question 2 — challenge a core business model assumption using something specific in the deck", "answer": ""},
    {"question": "Question 3 — ask about product differentiation vs current alternatives or competitors", "answer": ""},
    {"question": "Question 4 — ask about traction quality, retention, cohort, or revenue proof", "answer": ""},
    {"question": "Question 5 — ask about GTM efficiency or customer acquisition model", "answer": ""},
    {"question": "Question 6 — ask about scalability or operational bottlenecks", "answer": ""},
    {"question": "Question 7 — ask about why now / market timing", "answer": ""},
    {"question": "Question 8 — ask about fundraising use of funds or milestones", "answer": ""},
    {"question": "Question 9 — ask about next critical execution risk", "answer": ""},
    {"question": "Question 10 — any sharp investor diligence question triggered by the deck", "answer": ""}
  ]
}

Rules:
- Think deeply before answering. Prefer insight over repetition.
- Use evidence from the deck wherever possible.
- If the deck makes claims, test them logically instead of repeating them.
- Compare the startup implicitly or explicitly against likely alternatives already in the market.
- Identify what is missing, not only what is present.
- business_model and industry_context must be specific, nuanced, and useful to an investor unfamiliar with the sector.
- key_risks must contain 4–5 items only. Each should be concrete, non-generic, and tied to this deck.
- founder_questions must contain 7–10 items only, each as {"question":"","answer":""}.
- Order founder_questions by investment priority: legal/structure first, then business model truth-testing, then traction, then growth.
- Questions must be sharp, specific, and reference something concrete from the deck. They should probe assumptions, not ask for generic information.
- Do not invent facts not supported by the deck. Where uncertain, state the uncertainty.
- No scoring, no hype, no compliments.
- Return only raw JSON. No markdown fences. No text before or after the JSON."""


def analyze_deck(pdf_path: str, prefs) -> dict:
    """Upload PDF to OpenAI Files API and run VC analysis. Returns parsed result dict."""
    with open(pdf_path, 'rb') as f:
        uploaded_file = client.files.create(file=f, purpose='assistants')

    file_id = uploaded_file.id

    system_msg = SYSTEM_PROMPT.format(
        sectors_focus=getattr(prefs, 'sectors_focus', '') if prefs else '',
        stage_focus=getattr(prefs, 'stage_focus', '') if prefs else '',
        question_style=getattr(prefs, 'question_style', '') if prefs else '',
        additional_context=getattr(prefs, 'additional_context', '') if prefs else '',
    )

    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {'role': 'system', 'content': system_msg},
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': USER_PROMPT},
                    {'type': 'file', 'file': {'file_id': file_id}},
                ],
            },
        ],
    )

    raw = response.choices[0].message.content.strip()
    result = json.loads(raw)
    result['openai_file_id'] = file_id
    return result
