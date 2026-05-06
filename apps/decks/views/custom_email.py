from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.decks.models import Deck
from services.email_service import send_custom_email


class CustomEmailView(APIView):
    def post(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)

        recipients = request.data.get('recipients', [])
        body = request.data.get('body', '').strip()
        startup_name = request.data.get('startup_name', deck.startup_name)

        if not recipients:
            return Response({'error': 'At least one recipient is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not body:
            return Response({'error': 'Email body is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            for recipient in recipients:
                send_custom_email(recipient, startup_name, body)
        except Exception as e:
            return Response({'error': f'Email failed: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Email sent successfully.'})
