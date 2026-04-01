# Deck views: list all decks, upload + trigger async analysis pipeline, retrieve detail, email questions.

import os
import threading
from pathlib import Path

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser

from .models import Deck
from .serializers import DeckListSerializer, DeckDetailSerializer
from apps.setup.models import FirmPreferences
from services.conversion_service import convert_to_pdf
from services.storage_service import upload_to_cloudinary
from services.openai_service import analyze_deck
from services.email_service import send_founder_questions


def _run_analysis(deck_id: str, pdf_path: str):
    """Background thread: runs OpenAI analysis, uploads to Cloudinary, saves results. Cleans up temp file at the end."""
    from .models import Deck
    deck = Deck.objects.get(id=deck_id)
    try:
        # Get firm preferences
        prefs = FirmPreferences.objects.first()

        # Analyze with OpenAI (reads the local file)
        result = analyze_deck(pdf_path, prefs)

        # Upload to Cloudinary (file still exists)
        pdf_url = upload_to_cloudinary(pdf_path, f"decks/{deck_id}")

        deck.pdf_url = pdf_url
        deck.business_model = result['business_model']
        deck.industry_context = result['industry_context']
        deck.key_risks = result['key_risks']
        deck.founder_questions = result['founder_questions']
        deck.openai_file_id = result.get('openai_file_id', '')
        deck.status = 'complete'
        deck.save()
    except Exception as e:
        deck.status = 'failed'
        deck.error_message = str(e)
        deck.save(update_fields=['status', 'error_message'])
    finally:
        try:
            os.remove(pdf_path)
        except OSError:
            pass


class DeckListView(APIView):
    def get(self, request):
        decks = Deck.objects.all()
        return Response(DeckListSerializer(decks, many=True).data)


class DeckUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        ext = Path(file.name).suffix.lower()
        if ext not in ['.pdf', '.ppt', '.pptx']:
            return Response({'error': 'Only PDF, PPT, and PPTX files are accepted.'}, status=status.HTTP_400_BAD_REQUEST)

        startup_name = Path(file.name).stem.replace('_', ' ').replace('-', ' ').title()

        # Save uploaded file temporarily
        tmp_dir = Path('/tmp') if os.name != 'nt' else Path(os.environ.get('TEMP', 'C:/Temp'))
        tmp_dir.mkdir(exist_ok=True)
        tmp_path = tmp_dir / file.name
        with open(tmp_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        # Convert PPT/PPTX to PDF if needed
        if ext in ['.ppt', '.pptx']:
            try:
                pdf_path = convert_to_pdf(str(tmp_path))
                os.remove(tmp_path)
            except Exception as e:
                return Response({'error': f'PPT conversion failed: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            pdf_path = str(tmp_path)

        deck = Deck.objects.create(
            startup_name=startup_name,
            original_filename=file.name,
            status='processing',
            uploaded_by=request.user,
        )

        thread = threading.Thread(target=_run_analysis, args=(str(deck.id), pdf_path), daemon=True)
        thread.start()

        return Response({'id': str(deck.id), 'status': 'processing'}, status=status.HTTP_202_ACCEPTED)


class DeckDetailView(APIView):
    def get(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(DeckDetailSerializer(deck).data)


class DeckEmailView(APIView):
    def post(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)

        recipient = request.data.get('recipient_email', '').strip()
        if not recipient:
            return Response({'error': 'recipient_email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not deck.founder_questions:
            return Response({'error': 'No founder questions available.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            send_founder_questions(recipient, deck.startup_name, deck.founder_questions)
        except Exception as e:
            return Response({'error': f'Email failed: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Email sent successfully.'})
