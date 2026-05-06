import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.decks.models import Deck
from apps.setup.models import Prompt
from services.openai_service import client


class DealInsightView(APIView):
    def get(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)
        if deck.insight:
            return Response(deck.insight)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def post(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)

        system_prompt = Prompt.objects.get(key='insight_system').body
        user_prompt = Prompt.objects.get(key='insight_user').body

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
        team_comments = list(deck.comments.values_list('body', flat=True))
        if team_comments:
            extra_parts.append('[Team Notes]\n' + '\n'.join(f'- {c}' for c in team_comments))
        material_names = list(deck.materials.values_list('name', flat=True))
        if material_names:
            extra_parts.append('[Uploaded Files]\n' + '\n'.join(f'- {n}' for n in material_names))
        extra_notes_text = '\n\n'.join(extra_parts) or 'None available.'

        key_risks_text = '\n'.join(f'- {r}' for r in (deck.key_risks or []))
        industry_text = json.dumps(deck.industry_context) if isinstance(deck.industry_context, dict) else (deck.industry_context or 'Not available.')

        prompt = user_prompt.format(
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
                    {'role': 'system', 'content': system_prompt},
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

        deck.insight = insight
        deck.save(update_fields=['insight'])

        return Response(insight)
