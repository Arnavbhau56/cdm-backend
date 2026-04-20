# Deck CRUD views: list with filters, retrieve single deck, delete single deck, bulk delete.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.decks.models import Deck
from apps.decks.serializers import DeckListSerializer, DeckDetailSerializer


class DeckListView(APIView):
    def get(self, request):
        qs = Deck.objects.all()
        sector = request.query_params.get('sector')
        crm_status = request.query_params.get('crm_status')
        if sector:
            qs = qs.filter(sector__icontains=sector)
        if crm_status:
            qs = qs.filter(crm_status=crm_status)
        return Response(DeckListSerializer(qs, many=True).data)


class DeckDetailView(APIView):
    def get(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DeckDetailSerializer(deck).data)

    def delete(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)
        deck.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DeckBulkDeleteView(APIView):
    def post(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'No ids provided.'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = Deck.objects.filter(id__in=ids).delete()
        return Response({'deleted': deleted})
