import json
import requests as http_requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.decks.models import Deck
from apps.setup.models import Prompt
from services.openai_service import client


def _fetch_material_content(url: str, name: str) -> str:
    """Fetch text content of a material file from its URL. Returns empty string on failure."""
    try:
        r = http_requests.get(url, timeout=15)
        r.raise_for_status()
        # Try to decode as text; skip binary files
        return r.content.decode('utf-8', errors='ignore')
    except Exception:
        return ''


def _build_materials_context(deck) -> str:
    materials = list(deck.materials.all())
    if not materials:
        return 'No additional materials.'
    parts = []
    for m in materials:
        content = _fetch_material_content(m.url, m.name)
        if content.strip():
            parts.append(f'[{m.name}]\n{content.strip()}')
        else:
            parts.append(f'[{m.name}] (binary/unreadable file)')
    return '\n\n'.join(parts)


def run_auto_answer(deck) -> dict:
    if not deck.founder_questions:
        return {'founder_questions': deck.founder_questions, 'updated': 0}

    system_prompt = Prompt.objects.get(key='auto_answer_system').body
    user_prompt = Prompt.objects.get(key='auto_answer_user').body

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

    key_risks_text = '\n'.join(f'- {r}' for r in (deck.key_risks or []))
    questions_text = '\n'.join(f'{i}. {q["question"]}' for i, q in enumerate(deck.founder_questions))

    fmt_vars = dict(
        startup_name=deck.startup_name,
        business_model=deck.business_model or 'Not available.',
        industry_context=deck.industry_context or 'Not available.',
        key_risks=key_risks_text or 'Not available.',
        call_notes=call_notes_text,
        notes_context=notes_context,
        materials_context=materials_context,
        questions=questions_text,
    )
    prompt = user_prompt.format_map(fmt_vars)

    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': prompt},
        ],
        temperature=0,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith('```'):
        raw = raw.split('\n', 1)[1].rsplit('```', 1)[0].strip()
    answers = json.loads(raw)

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
    return {'founder_questions': deck.founder_questions, 'updated': updated}


class AutoAnswerView(APIView):
    def post(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)

        if not deck.founder_questions:
            return Response({'error': 'No questions to answer.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = run_auto_answer(deck)
        except Exception as e:
            return Response({'error': f'OpenAI error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(result)
