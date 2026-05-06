import json
import requests as http_requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.decks.models import Deck
from apps.setup.models import Prompt
from services.openai_service import client
from apps.decks.views.auto_answer import _build_materials_context


class SuggestQuestionsView(APIView):
    def post(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)

        prompt = (request.data.get('prompt') or '').strip()
        if not prompt:
            return Response({'error': 'prompt is required.'}, status=status.HTTP_400_BAD_REQUEST)

        system_prompt = Prompt.objects.get(key='suggest_questions_system').body
        user_prompt = Prompt.objects.get(key='suggest_questions_user').body

        existing = '\n'.join(
            f'- {q["question"]}' for q in (deck.founder_questions or [])
        ) or 'None yet.'

        key_risks_text = '\n'.join(f'- {r}' for r in (deck.key_risks or []))

        call_notes_text = ''
        if deck.call_notes:
            for key, val in deck.call_notes.items():
                if val and val.strip():
                    call_notes_text += f'{key.replace("_", " ").title()}:\n{val.strip()}\n\n'
        if not call_notes_text:
            call_notes_text = 'No call notes available.'

        notes_context = ''
        for note in deck.notes.all():
            label = note.title or note.get_kind_display()
            notes_context += f'[{label}]\n{note.body.strip()}\n\n'
        if not notes_context:
            notes_context = 'No notes available.'

        materials_context = _build_materials_context(deck)

        fmt_vars = dict(
            startup_name=deck.startup_name,
            sector=deck.sector or 'Unknown',
            business_model=deck.business_model or 'Not available.',
            industry_context=deck.industry_context or 'Not available.',
            key_risks=key_risks_text or 'Not available.',
            call_notes=call_notes_text,
            notes_context=notes_context,
            materials_context=materials_context,
            existing_questions=existing,
            prompt=prompt,
        )
        user_msg = user_prompt.format_map(fmt_vars)

        try:
            response = client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {'role': 'system', 'content': system_prompt},
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
            # Normalize to ensure each has question and sector
            normalized = []
            for s in suggestions:
                if isinstance(s, dict) and 'question' in s:
                    normalized.append({'question': str(s['question']), 'sector': str(s.get('sector', ''))})
                elif isinstance(s, str):
                    normalized.append({'question': s, 'sector': ''})
            suggestions = normalized
        except Exception as e:
            return Response({'error': f'OpenAI error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'suggestions': suggestions})
