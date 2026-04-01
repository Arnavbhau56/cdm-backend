# OpenAI service: uploads PDF to Files API, calls gpt-4o with structured VC analysis prompt,
# and returns parsed JSON with business_model, industry_context, key_risks, founder_questions.

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

A startup pitch deck has been attached as a file. Your job is NOT to summarize the deck.
Your job is to help our investment team deeply understand this business and walk into
the first founder call fully prepared — even if they have never seen this sector before.

Return ONLY a valid JSON object with exactly these 4 keys. No markdown. No explanation outside the JSON."""

USER_PROMPT = """Analyze the attached pitch deck and return this exact JSON structure:

{
  "business_model": "A clear, jargon-free explanation of what this company does, who their customer is, how they make money, and why a customer would choose them over alternatives. Write as if explaining to a smart generalist who knows nothing about this sector.",

  "industry_context": "Explain how this type of business typically works — the category dynamics, what drives success in it, how companies in this space typically grow, and any relevant VC-backed precedents or comparable companies.",

  "key_risks": [
    "Risk 1 — explain the exact mechanism of why this is a risk. Reference specific data or gaps from the deck.",
    "Risk 2...",
    "Risk 3...",
    "Risk 4...",
    "Risk 5..."
  ],

  "founder_questions": [
    "Question 1 — reference something specific from the deck",
    "Question 2...",
    "...up to 10 questions, ordered by investment priority"
  ]
}

Rules:
- key_risks must have 4–5 items. Each must explain the mechanism and reference something specific in this deck.
- founder_questions must have 7–10 items, ordered: legal/structural risks first, then business model assumptions, then growth.
- Do not invent information not present in the deck.
- Do not score, grade, or rank the startup in any way.
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
