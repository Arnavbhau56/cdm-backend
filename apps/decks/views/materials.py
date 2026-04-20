# Materials views: upload, list, and delete additional files (financials, term sheets, etc.) per deck.

import os
import tempfile

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser

from apps.decks.models import Deck, DeckMaterial
from apps.decks.serializers import DeckMaterialSerializer
from services.storage_service import upload_to_cloudinary


class DeckMaterialView(APIView):
    parser_classes = [MultiPartParser]

    def get(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DeckMaterialSerializer(deck.materials.all(), many=True).data)

    def post(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)

        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        suffix = os.path.splitext(file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            url = upload_to_cloudinary(tmp_path, f'materials/{pk}/{file.name}')
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

        material = DeckMaterial.objects.create(
            deck=deck, name=file.name, url=url, uploaded_by=request.user
        )
        return Response(DeckMaterialSerializer(material).data, status=status.HTTP_201_CREATED)


class DeckMaterialDeleteView(APIView):
    def delete(self, request, pk, material_id):
        try:
            material = DeckMaterial.objects.get(id=material_id, deck_id=pk)
        except DeckMaterial.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        material.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
