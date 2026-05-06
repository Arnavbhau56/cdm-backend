from django.db import migrations

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

Call Notes:
{call_notes}

Additional Notes:
{notes_context}

Additional Materials:
{materials_context}

Existing questions (do NOT repeat these):
{existing_questions}

---

Analyst's focus for new questions:
\"{prompt}\"

Generate 4–6 new investor-grade questions based on the focus above and the deck context.
Each question MUST be assigned to one of these sectors:
- Problem and Product
- Business Model
- Market and GTM
- Financials and Traction
- Growth and Technology
- Legal and Compliance

Return a JSON array where each item has:
{{
  "question": "the question text",
  "sector": "one of the 6 sectors above"
}}

No numbering. No markdown. Raw JSON array only."""

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
  "stage_rationale": "2-3 crisp bullet points explaining why this stage label fits. Reference specific evidence — product status, revenue numbers, team size, or lack thereof. Format as separate sentences that will be displayed as bullet points.",

  "ratings": [
    {{
      "dimension": "Founder",
      "score": "Strong | Promising | Early | Weak | Unclear",
      "rationale": "2-4 crisp bullet points. Assess: does the founder come from directly relevant domain experience? How many years? Have they put in personal capital (skin in the game)? Have they built or scaled anything before? Be specific about what is known and what is missing. Format as separate sentences that will be displayed as bullet points."
    }},
    {{
      "dimension": "TAM",
      "score": "Strong | Promising | Early | Weak | Unclear",
      "rationale": "2-4 crisp bullet points. Is the addressable market large enough to support a venture-scale outcome? Are there large US or global players already building in this space (signals validation)? Give a number if available. Flag if the TAM is niche, crowded, or structurally capped. Format as separate sentences that will be displayed as bullet points."
    }},
    {{
      "dimension": "Problem Quality",
      "score": "Strong | Promising | Early | Weak | Unclear",
      "rationale": "2-4 crisp bullet points. Is this solving a must-have problem or a nice-to-have? Is the pain acute and frequent for the target customer? Is there evidence of pull (customers seeking this out) vs push (founders convincing customers they have a problem)? Format as separate sentences that will be displayed as bullet points."
    }},
    {{
      "dimension": "Business Model",
      "score": "Strong | Promising | Early | Weak | Unclear",
      "rationale": "2-4 crisp bullet points. Is the revenue model clear and defensible? Is there a logical path to scale? Are there structural risks in how they make money? Format as separate sentences that will be displayed as bullet points."
    }},
    {{
      "dimension": "Unit Economics",
      "score": "Strong | Promising | Early | Weak | Unclear",
      "rationale": "2-4 crisp bullet points. What is the pricing vs estimated CAC? Is the model profitable at the unit level from day one, or does it require scale to work? If numbers are not in the deck, flag what is missing and what the model implies. Format as separate sentences that will be displayed as bullet points."
    }},
    {{
      "dimension": "Traction",
      "score": "Strong | Promising | Early | Weak | Unclear",
      "rationale": "2-4 crisp bullet points. What concrete evidence of traction exists — revenue, users, pilots, LOIs, growth rate? Is it real revenue or vanity metrics? Is retention visible? Format as separate sentences that will be displayed as bullet points."
    }},
    {{
      "dimension": "GTM",
      "score": "Strong | Promising | Early | Weak | Unclear",
      "rationale": "2-4 crisp bullet points. Is the go-to-market strategy credible and capital-efficient? Is there a clear first beachhead? Does the team have the distribution relationships to execute it? Format as separate sentences that will be displayed as bullet points."
    }}
  ],

  "key_metrics": [
    {{"label": "metric name", "value": "value or N/A"}}
  ],

  "comparables": [
    {{"name": "Company name", "geography": "US / India / Global", "note": "1 line on relevance or outcome"}}
  ],

  "overall_score": 0,

  "score_rationale": "2-3 sentences explaining the overall score. What is the single biggest thing holding this back, and what would need to be true to move the score up significantly?",

  "recommendation": "One of: Pass / Watch / Soft Interest / Take Meeting / Fast Track",

  "recommendation_rationale": "2-3 crisp bullet points on why this recommendation. What is the key open question that would change the recommendation? Format as separate sentences that will be displayed as bullet points.",

  "one_line_verdict": "One sharp sentence summarising the deal for a partner who has 10 seconds."
}}

Rules:
- overall_score: integer 0-100. Weight the dimensions roughly: Founder 25%, TAM 15%, Problem Quality 15%, Business Model 15%, Unit Economics 10%, Traction 15%, GTM 5%. Be honest — most early-stage decks score 35-60. Reserve 75+ for genuinely strong deals.
- key_metrics: extract any numbers mentioned (ARR, MRR, GMV, burn, runway, CAC, LTV, headcount, revenue, growth rate, pricing). Include up to 8. If none found, return empty array.
- comparables: name 2-4 real companies in the same space — include at least one from India and one from the US if the sector has them.
- ratings scores must use ONLY the allowed values listed.
- If data is genuinely missing for a dimension, use \"Unclear\".
- IMPORTANT: For stage_rationale, recommendation_rationale, and all dimension rationales, write 2-4 separate complete sentences. Each sentence will be displayed as a bullet point in the UI. Do NOT use actual bullet point symbols or numbering.
- Return only raw JSON. No markdown fences."""


def seed_extra_prompts(apps, schema_editor):
    Prompt = apps.get_model('setup', 'Prompt')
    extras = [
        ('auto_answer_system', 'Auto Answer — System', AUTO_ANSWER_SYSTEM),
        ('auto_answer_user', 'Auto Answer — User', AUTO_ANSWER_USER),
        ('suggest_questions_system', 'Suggest Questions — System', SUGGEST_SYSTEM),
        ('suggest_questions_user', 'Suggest Questions — User', SUGGEST_USER),
        ('insight_system', 'Deal Insight — System', INSIGHT_SYSTEM),
        ('insight_user', 'Deal Insight — User', INSIGHT_USER),
    ]
    for key, title, body in extras:
        obj, created = Prompt.objects.get_or_create(key=key, defaults={'title': title, 'body': body})
        if not created:
            obj.body = body
            obj.save()


class Migration(migrations.Migration):
    dependencies = [
        ('setup', '0002_prompt'),
    ]

    operations = [
        migrations.RunPython(seed_extra_prompts, reverse_code=migrations.RunPython.noop),
    ]
