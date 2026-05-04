# Deal insight view: synthesises deck analysis, call notes, and all text notes into a
# structured intelligence brief — stage rating, dimension scores, key metrics, comparables.

import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.decks.models import Deck
from services.openai_service import client

SYSTEM_PROMPT = """You are a senior VC analyst at CDM Capital producing a structured deal intelligence brief.
You will be given everything known about a startup: deck analysis, call notes, and any additional notes (MIS, WhatsApp, financials).
Your job is to synthesise this into a concise, honest, investor-grade snapshot.
Be direct. Use numbers where present. Do not invent data not in the context.
Return only raw JSON — no markdown, no explanation."""

USER_PROMPT = """Startup: {startup_name}
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
  "stage_rationale": "2-3 sentences explaining why this stage label fits. Reference specific evidence — product status, revenue numbers, team size, or lack thereof.",

  "ratings": [
    {{
      "dimension": "Founder",
      "score": "Strong | Promising | Early | Weak | Unclear",
      "rationale": "Assess: does the founder come from directly relevant domain experience? How many years? Have they put in personal capital (skin in the game)? Have they built or scaled anything before? Be specific about what is known and what is missing."
    }},
    {{
      "dimension": "TAM",
      "score": "Strong | Promising | Early | Weak | Unclear",
      "rationale": "Is the addressable market large enough to support a venture-scale outcome? Are there large US or global players already building in this space (signals validation)? Give a number if available. Flag if the TAM is niche, crowded, or structurally capped."
    }},
    {{
      "dimension": "Problem Quality",
      "score": "Strong | Promising | Early | Weak | Unclear",
      "rationale": "Is this solving a must-have problem or a nice-to-have? Is the pain acute and frequent for the target customer? Is there evidence of pull (customers seeking this out) vs push (founders convincing customers they have a problem)?"
    }},
    {{
      "dimension": "Business Model",
      "score": "Strong | Promising | Early | Weak | Unclear",
      "rationale": "Is the revenue model clear and defensible? Is there a logical path to scale? Are there structural risks in how they make money?"
    }},
    {{
      "dimension": "Unit Economics",
      "score": "Strong | Promising | Early | Weak | Unclear",
      "rationale": "What is the pricing vs estimated CAC? Is the model profitable at the unit level from day one, or does it require scale to work? If numbers are not in the deck, flag what is missing and what the model implies."
    }},
    {{
      "dimension": "Traction",
      "score": "Strong | Promising | Early | Weak | Unclear",
      "rationale": "What concrete evidence of traction exists — revenue, users, pilots, LOIs, growth rate? Is it real revenue or vanity metrics? Is retention visible?"
    }},
    {{
      "dimension": "GTM",
      "score": "Strong | Promising | Early | Weak | Unclear",
      "rationale": "Is the go-to-market strategy credible and capital-efficient? Is there a clear first beachhead? Does the team have the distribution relationships to execute it?"
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

  "recommendation_rationale": "2-3 sentences on why this recommendation. What is the key open question that would change the recommendation?",

  "one_line_verdict": "One sharp sentence summarising the deal for a partner who has 10 seconds."
}}

Rules:
- overall_score: integer 0-100. Weight the dimensions roughly: Founder 25%, TAM 15%, Problem Quality 15%, Business Model 15%, Unit Economics 10%, Traction 15%, GTM 5%. Be honest — most early-stage decks score 35-60. Reserve 75+ for genuinely strong deals.
- key_metrics: extract any numbers mentioned (ARR, MRR, GMV, burn, runway, CAC, LTV, headcount, revenue, growth rate, pricing). Include up to 8. If none found, return empty array.
- comparables: name 2-4 real companies in the same space — include at least one from India and one from the US if the sector has them.
- ratings scores must use ONLY the allowed values listed.
- If data is genuinely missing for a dimension, use \"Unclear\".
- Return only raw JSON. No markdown fences."""


class DealInsightView(APIView):
    def post(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)

        call_notes_text = ''
        if deck.call_notes:
            for key, val in deck.call_notes.items():
                if val and val.strip():
                    call_notes_text += f'{key.replace("_", " ").title()}:\n{val.strip()}\n\n'
        call_notes_text = call_notes_text.strip() or 'None available.'

        extra_parts = []
        for note in deck.notes.all():
            label = dict(deck.notes.model.KIND_CHOICES).get(note.kind, note.kind)
            title = f' — {note.title}' if note.title else ''
            extra_parts.append(f'[{label}{title}]\n{note.body}')
        material_names = list(deck.materials.values_list('name', flat=True))
        if material_names:
            extra_parts.append('[Uploaded Files]\n' + '\n'.join(f'- {n}' for n in material_names))
        extra_notes_text = '\n\n'.join(extra_parts) or 'None available.'

        key_risks_text = '\n'.join(f'- {r}' for r in (deck.key_risks or []))
        industry_text = json.dumps(deck.industry_context) if isinstance(deck.industry_context, dict) else (deck.industry_context or 'Not available.')

        prompt = USER_PROMPT.format(
            startup_name=deck.startup_name,
            sector=deck.sector or 'Unknown',
            business_model=deck.business_model or 'Not available.',
            industry_context=industry_text,
            key_risks=key_risks_text or 'Not available.',
            call_notes=call_notes_text,
            extra_notes=extra_notes_text,
        )

        try:
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {'role': 'system', 'content': SYSTEM_PROMPT},
                    {'role': 'user', 'content': prompt},
                ],
                temperature=0,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith('```'):
                raw = raw.split('\n', 1)[1].rsplit('```', 1)[0].strip()
            insight = json.loads(raw)
        except Exception as e:
            return Response({'error': f'OpenAI error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(insight)
