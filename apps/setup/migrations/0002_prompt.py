from django.db import migrations, models

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


AUTO_ANSWER_SYSTEM = """You are an analyst helping a VC firm find answers to founder questions.
You are given context from a startup's pitch deck analysis, call notes, and any additional materials uploaded.
Your job is to look through ALL provided context and find answers ONLY if the information is explicitly present.
Do NOT invent, infer, or guess. If the answer is not clearly present in the context, return null for that question.
Be concise. Quote or paraphrase directly from the context."""

AUTO_ANSWER_USER = """Here is the context about the startup "{startup_name}":

--- DECK ANALYSIS ---
Business Model: {business_model}

Industry Context: {industry_context}

Key Risks:
{key_risks}

--- CALL NOTES ---
{call_notes}

--- ADDITIONAL MATERIALS ---
{materials_context}

---

Now answer the following questions using ONLY the context above.
Return a JSON array where each item has:
- "index": the question index (integer)
- "answer": the answer string if found in context, or null if not found

Questions:
{questions}

Return only raw JSON array. No markdown. No explanation."""

SUGGEST_SYSTEM = """You are a senior VC analyst at CDM Capital generating additional diligence questions for a founder meeting.
You have full context on the startup from its pitch deck analysis.
Generate sharp, specific, non-generic questions that probe assumptions, expose risks, or surface missing information.
Each question must be directly grounded in the deck context — never ask for information already answered in the analysis.
Do not repeat questions that already exist."""

SUGGEST_USER = """Startup: {startup_name}
Sector: {sector}

Business Model:
{business_model}

Industry Context:
{industry_context}

Key Risks:
{key_risks}

Existing questions (do NOT repeat these):
{existing_questions}

---

Analyst's focus for new questions:
\"{prompt}\"

Generate 4–6 new investor-grade questions based on the focus above and the deck context.
Return a JSON array of strings — each item is one question. No numbering. No markdown. Raw JSON array only."""

INSIGHT_SYSTEM = """You are a senior VC analyst at CDM Capital producing a structured deal intelligence brief.
You will be given everything known about a startup: deck analysis, call notes, and any additional notes (MIS, WhatsApp, financials).
Your job is to synthesise this into a concise, honest, investor-grade snapshot.
Be direct. Use numbers where present. Do not invent data not in the context.
Return only raw JSON — no markdown, no explanation."""

INSIGHT_USER = """Startup: {startup_name}
Sector: {sector}

--- DECK ANALYSIS ---
Business Model: {business_model}
Industry Context: {industry_context}
Key Risks:
{key_risks}

--- CALL NOTES ---
{call_notes}

--- ADDITIONAL NOTES (MIS / WhatsApp / General) ---
{extra_notes}

---

Produce a JSON object with exactly these keys:

{{
  "stage_label": "One of: Pre-Idea / Pre-Product / Pre-Revenue / Early Revenue / Growth / Scaling",
  "stage_rationale": "2-3 sentences explaining why this stage label fits.",
  "ratings": [
    {{"dimension": "Founder", "score": "Strong | Promising | Early | Weak | Unclear", "rationale": "..."}},
    {{"dimension": "TAM", "score": "Strong | Promising | Early | Weak | Unclear", "rationale": "..."}},
    {{"dimension": "Problem Quality", "score": "Strong | Promising | Early | Weak | Unclear", "rationale": "..."}},
    {{"dimension": "Business Model", "score": "Strong | Promising | Early | Weak | Unclear", "rationale": "..."}},
    {{"dimension": "Unit Economics", "score": "Strong | Promising | Early | Weak | Unclear", "rationale": "..."}},
    {{"dimension": "Traction", "score": "Strong | Promising | Early | Weak | Unclear", "rationale": "..."}},
    {{"dimension": "GTM", "score": "Strong | Promising | Early | Weak | Unclear", "rationale": "..."}}
  ],
  "key_metrics": [{{"label": "metric name", "value": "value or N/A"}}],
  "comparables": [{{"name": "Company name", "geography": "US / India / Global", "note": "1 line on relevance or outcome"}}],
  "overall_score": 0,
  "score_rationale": "2-3 sentences explaining the overall score.",
  "recommendation": "One of: Pass / Watch / Soft Interest / Take Meeting / Fast Track",
  "recommendation_rationale": "2-3 sentences on why this recommendation.",
  "one_line_verdict": "One sharp sentence summarising the deal."
}}

Rules:
- overall_score: integer 0-100. Weight: Founder 25%, TAM 15%, Problem Quality 15%, Business Model 15%, Unit Economics 10%, Traction 15%, GTM 5%.
- key_metrics: extract any numbers mentioned. Include up to 8. If none found, return empty array.
- comparables: name 2-4 real companies in the same space.
- ratings scores must use ONLY the allowed values listed.
- If data is genuinely missing for a dimension, use \"Unclear\".
- Return only raw JSON. No markdown fences."""


def seed_prompts(apps, schema_editor):
    Prompt = apps.get_model('setup', 'Prompt')
    Prompt.objects.get_or_create(
        key='system_prompt',
        defaults={'title': 'System Prompt', 'body': SYSTEM_PROMPT},
    )
    Prompt.objects.get_or_create(
        key='user_prompt',
        defaults={'title': 'User Prompt', 'body': USER_PROMPT},
    )
    Prompt.objects.get_or_create(
        key='auto_answer_system',
        defaults={'title': 'Auto Answer — System', 'body': AUTO_ANSWER_SYSTEM},
    )
    Prompt.objects.get_or_create(
        key='auto_answer_user',
        defaults={'title': 'Auto Answer — User', 'body': AUTO_ANSWER_USER},
    )
    Prompt.objects.get_or_create(
        key='suggest_questions_system',
        defaults={'title': 'Suggest Questions — System', 'body': SUGGEST_SYSTEM},
    )
    Prompt.objects.get_or_create(
        key='suggest_questions_user',
        defaults={'title': 'Suggest Questions — User', 'body': SUGGEST_USER},
    )
    Prompt.objects.get_or_create(
        key='insight_system',
        defaults={'title': 'Deal Insight — System', 'body': INSIGHT_SYSTEM},
    )
    Prompt.objects.get_or_create(
        key='insight_user',
        defaults={'title': 'Deal Insight — User', 'body': INSIGHT_USER},
    )


class Migration(migrations.Migration):
    dependencies = [
        ('setup', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prompt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=50, unique=True)),
                ('title', models.CharField(max_length=100)),
                ('body', models.TextField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RunPython(seed_prompts, reverse_code=migrations.RunPython.noop),
    ]
