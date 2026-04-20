# Auto-answer view: uses GPT-4o to find answers to founder questions
# strictly from the deck analysis and call notes context. Never hallucates.

import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.decks.models import Deck
from services.openai_service import client

SYSTEM_PROMPT = """You are an analyst helping a VC firm find answers to founder questions.
You are given context from a startup's pitch deck analysis and call notes.
Your job is to look through the context and find answers ONLY if the information is explicitly present.
Do NOT invent, infer, or guess. If the answer is not clearly present in the context, return null for that question.
Be concise. Quote or paraphrase directly from the context."""

USER_PROMPT = """Here is the context about the startup "{startup_name}":

--- DECK ANALYSIS ---
Business Model: {business_model}

Industry Context: {industry_context}

Key Risks:
{key_risks}

--- CALL NOTES ---
{call_notes}

---

Now answer the following questions using ONLY the context above.
Return a JSON array where each item has:
- "index": the question index (integer)
- "answer": the answer string if found in context, or null if not found

Questions:
{questions}

Return only raw JSON array. No markdown. No explanation."""


class AutoAnswerView(APIView):
    def post(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not deck.founder_questions:
            return Response({'error': 'No questions to answer.'}, status=status.HTTP_400_BAD_REQUEST)

        # Build call notes block
        call_notes_text = ''
        if deck.call_notes:
            for key, val in deck.call_notes.items():
                if val and val.strip():
                    label = key.replace('_', ' ').title()
                    call_notes_text += f'{label}:\n{val.strip()}\n\n'
        if not call_notes_text:
            call_notes_text = 'No call notes available.'

        key_risks_text = '\n'.join(f'- {r}' for r in (deck.key_risks or []))

        questions_text = '\n'.join(
            f'{i}. {q["question"]}'
            for i, q in enumerate(deck.founder_questions)
        )

        prompt = USER_PROMPT.format(
            startup_name=deck.startup_name,
            business_model=deck.business_model or 'Not available.',
            industry_context=deck.industry_context or 'Not available.',
            key_risks=key_risks_text or 'Not available.',
            call_notes=call_notes_text,
            questions=questions_text,
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
            # Strip markdown fences if present
            if raw.startswith('```'):
                raw = raw.split('\n', 1)[1].rsplit('```', 1)[0].strip()
            answers = json.loads(raw)
        except Exception as e:
            return Response({'error': f'OpenAI error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Merge answers back — only update questions where answer was found
        updated = 0
        questions = list(deck.founder_questions)
        for item in answers:
            idx = item.get('index')
            answer = item.get('answer')
            if answer and isinstance(idx, int) and 0 <= idx < len(questions):
                questions[idx]['answer'] = answer
                updated += 1

        deck.founder_questions = questions
        deck.save(update_fields=['founder_questions'])

        return Response({
            'founder_questions': deck.founder_questions,
            'updated': updated,
        })
