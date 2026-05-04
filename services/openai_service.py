# OpenAI service: uploads PDF to Files API, calls gpt-4o with structured VC analysis prompt,
# returns parsed JSON with startup_name, sector, founder_email, business_model, industry_context, key_risks, founder_questions.

import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

SYSTEM_PROMPT = """You are a senior venture capital analyst working for CDM Capital, an early-stage VC firm.

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

Return ONLY a valid JSON object with exactly these 10 keys. No markdown. No explanation outside the JSON."""

USER_PROMPT = """Analyze the attached pitch deck and return this exact JSON structure:

{
  "startup_name": "The exact brand/trading name of the startup as it appears in the deck.",

  "registered_name": "The legal registered company name (e.g. Acme Technologies Private Limited). If not explicitly stated in the deck, make a best-effort inference from any legal notices, footer text, or incorporation details shown. If truly not found, return empty string.",

  "sector": "Primary sector label only (e.g. Fintech or Healthtech or SaaS). Single label, no commas.",

  "sub_sector": "2-3 more specific sub-sector or theme tags, comma-separated (e.g. Lending, B2B, Embedded Finance).",

  "one_liner": "One crisp sentence (max 20 words) describing what the company does and for whom. No hype.",

  "founder_email": "Email address of the founder or company contact if present in the deck. If not found, return empty string.",

  "business_model": "Write a sharp investor-grade explanation of what the company does, who pays them, how revenue is generated, what customer workflow they fit into, why customers would switch from current alternatives, and what must happen for revenue to scale materially. Avoid generic wording.",

  "industry_context": {
    "value_chain_position": "Be precise and layered. First name the macro industry (e.g. Fintech). Then name the sub-vertical within it (e.g. WealthTech > Retail Investment Platforms). Then map the full value chain top-to-bottom: who are the upstream providers (data, infrastructure, capital, regulation), who are the platform/middleware layer, who are the product/distribution layer, and who are the end customers. State exactly which layer this startup occupies, what they depend on upstream, and who they compete with or displace at their layer. One paragraph, dense and specific.",
    "market_size": "Give the India TAM and SAM with real numbers (cite the basis — e.g. RBI data, SEBI filings, industry reports, or your own bottom-up reasoning). Then give the global comparable market size. State the current penetration rate and the realistic addressable opportunity for a startup at this stage. Do not use vague ranges — give a specific number and explain how you arrived at it.",
    "market_timing": "What structural shifts — regulatory, technological, demographic, or behavioural — are creating the window right now? Name 2-3 specific tailwinds with dates or data points where possible. Also name 1 headwind or timing risk that could slow adoption.",
    "competitive_landscape": {
      "market_structure": "One paragraph: is this market fragmented or consolidated, winner-take-all or multi-player? Where does this startup sit relative to incumbents — attacking from below, above, or a different axis?",
      "competitors_india": [
        { "name": "Company name", "description": "What they do", "scale": "Revenue / users / funding if known", "relevance": "Direct competitor / indirect / adjacent" },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." }
      ],
      "competitors_global": [
        { "name": "Company name", "description": "What they do", "scale": "Revenue / users / funding if known", "relevance": "What happened to them / are they entering India" },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." },
        { "name": "...", "description": "...", "scale": "...", "relevance": "..." }
      ],
      "trends": [
        { "trend": "Trend name", "detail": "What is happening, why it matters for this space, and how it affects this startup specifically" },
        { "trend": "...", "detail": "..." },
        { "trend": "...", "detail": "..." }
      ]
    },
    "unit_economics": "What are the typical gross margins in this sub-sector and why (e.g. software layer vs. services layer vs. marketplace take rate)? What does a healthy CAC:LTV ratio look like here? What is the typical payback period? What does the P&L of a scaled player in this space look like — what are the dominant cost lines? If this startup's model implies different economics, flag the assumption.",
    "regulatory": "List the specific regulatory bodies, licenses, and compliance requirements relevant to this business in India (e.g. SEBI RIA license, RBI NBFC registration, IRDAI approval). Note any recent regulatory changes that help or hurt this model. Flag any regulatory risk that is not addressed in the deck.",
    "failure_modes": "Name 2-3 real companies in this space (India or global) that failed or struggled and explain precisely why — not generic reasons, but the specific mechanism of failure (e.g. unit economics collapse at scale, regulatory shutdown, distribution dependency, commoditisation). What assumptions do founders in this space consistently get wrong?",
    "winners_playbook": "What have the 1-2 category leaders in this space done that others have not? Is the moat distribution, data network effects, regulatory capture, product depth, or pricing? What does the path to category leadership look like — what milestones define it? What would need to be true for this startup to be on that path?"
  },

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
- business_model must be specific, nuanced, and useful to an investor unfamiliar with the sector.
- industry_context is a JSON object with 8 keys. Every text field must be substantive — minimum 3-4 sentences. competitive_landscape must contain real named companies with actual scale/funding data — do not use placeholder names. trends must contain 3-5 items. Name real companies. Give real numbers where known. This is the most important part of the output — do not truncate or genericise any field.
- key_risks must contain 4–5 items only. Each should be concrete, non-generic, and tied to this deck.
- founder_questions must contain 7–10 items only, each as {"question":"","answer":""}.
- Order founder_questions by investment priority: legal/structure first, then business model truth-testing, then traction, then growth.
- Questions must be sharp, specific, and reference something concrete from the deck. They should probe assumptions, not ask for generic information.
- Do not invent facts not supported by the deck. Where uncertain, state the uncertainty.
- No scoring, no hype, no compliments.
- Return only raw JSON. No markdown fences. No text before or after the JSON."""


def analyze_deck(pdf_path: str) -> dict:
    """Upload PDF to OpenAI Files API and run VC analysis. Returns parsed result dict."""
    with open(pdf_path, 'rb') as f:
        uploaded_file = client.files.create(file=f, purpose='assistants')

    file_id = uploaded_file.id

    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
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
