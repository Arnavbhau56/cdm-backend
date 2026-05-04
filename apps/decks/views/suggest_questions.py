# Suggest questions view: given a user prompt and deck context, generates additional
# sharp investor questions using GPT-4o. Returns suggestions only — not saved until accepted.

import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.decks.models import Deck
from services.openai_service import client

SYSTEM_PROMPT = """You are a senior VC analyst at CDM Capital generating additional diligence questions for a founder meeting.
You have full context on the startup from its pitch deck analysis.
Generate sharp, specific, non-generic questions that probe assumptions, expose risks, or surface missing information.
Each question must be directly grounded in the deck context — never ask for information already answered in the analysis.
Do not repeat questions that already exist."""

USER_PROMPT = """Startup: {startup_name}
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


class SuggestQuestionsView(APIView):
    def post(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)

        prompt = (request.data.get('prompt') or '').strip()
        if not prompt:
            return Response({'error': 'prompt is required.'}, status=status.HTTP_400_BAD_REQUEST)

        existing = '\n'.join(
            f'- {q["question"]}' for q in (deck.founder_questions or [])
        ) or 'None yet.'

        key_risks_text = '\n'.join(f'- {r}' for r in (deck.key_risks or []))

        user_msg = USER_PROMPT.format(
            startup_name=deck.startup_name,
            sector=deck.sector or 'Unknown',
            business_model=deck.business_model or 'Not available.',
            industry_context=deck.industry_context or 'Not available.',
            key_risks=key_risks_text or 'Not available.',
            existing_questions=existing,
            prompt=prompt,
        )

        try:
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {'role': 'system', 'content': SYSTEM_PROMPT},
                    {'role': 'user', 'content': user_msg},
                ],
                temperature=0.4,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith('```'):
                raw = raw.split('\n', 1)[1].rsplit('```', 1)[0].strip()
            suggestions = json.loads(raw)
            if not isinstance(suggestions, list):
                raise ValueError('Expected a JSON array')
        except Exception as e:
            return Response({'error': f'OpenAI error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'suggestions': [str(s) for s in suggestions if s]})
