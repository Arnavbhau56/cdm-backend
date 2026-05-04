# Notes views: create, list, delete free-text notes (general, MIS, WhatsApp, call) per deck.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.decks.models import Deck, DeckNote


class DeckNoteView(APIView):
    def get(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)
        notes = deck.notes.all()
        return Response([_serialize(n) for n in notes])

    def post(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)

        body = (request.data.get('body') or '').strip()
        if not body:
            return Response({'error': 'body is required.'}, status=status.HTTP_400_BAD_REQUEST)

        note = DeckNote.objects.create(
            deck=deck,
            kind=request.data.get('kind', 'general'),
            title=(request.data.get('title') or '').strip(),
            body=body,
            created_by=request.user,
        )
        return Response(_serialize(note), status=status.HTTP_201_CREATED)


class DeckNoteDeleteView(APIView):
    def delete(self, request, pk, note_id):
        try:
            note = DeckNote.objects.get(id=note_id, deck_id=pk)
        except DeckNote.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def _serialize(n: DeckNote) -> dict:
    return {
        'id': str(n.id),
        'kind': n.kind,
        'title': n.title,
        'body': n.body,
        'created_by': n.created_by.get_full_name() or n.created_by.username if n.created_by else 'Unknown',
        'created_at': n.created_at.isoformat(),
    }
