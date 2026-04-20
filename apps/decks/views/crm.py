# CRM views: update pipeline status, update founder email, save call notes.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.decks.models import Deck
from apps.decks.serializers import FounderContactSerializer

CALL_NOTE_SECTIONS = [
    'overview', 'problem', 'solution', 'product_business_model',
    'traction_metrics', 'founding_team', 'competition',
    'roadmap_gtm', 'fundraise_history',
]


class DeckCrmStatusView(APIView):
    def patch(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('crm_status', '').lower()
        valid = [c[0] for c in Deck.CRM_STATUS]
        if new_status not in valid:
            return Response({'error': f'crm_status must be one of {valid}.'}, status=status.HTTP_400_BAD_REQUEST)

        deck.crm_status = new_status
        deck.save(update_fields=['crm_status'])
        return Response({'crm_status': deck.crm_status})


class FounderContactView(APIView):
    def patch(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FounderContactSerializer(deck, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


class CallNotesView(APIView):
    def patch(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)

        notes = request.data.get('call_notes', {})
        if not isinstance(notes, dict):
            return Response({'error': 'call_notes must be an object.'}, status=status.HTTP_400_BAD_REQUEST)

        current = deck.call_notes or {}
        current.update({k: v for k, v in notes.items() if k in CALL_NOTE_SECTIONS})
        deck.call_notes = current
        deck.save(update_fields=['call_notes'])
        return Response({'call_notes': deck.call_notes})
