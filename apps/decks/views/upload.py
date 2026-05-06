# Deck upload view: receives file, converts PPT→PDF if needed, triggers background analysis pipeline.

import os
import threading
from pathlib import Path

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser

from apps.decks.models import Deck
from apps.decks.serializers import DeckDetailSerializer
from services.conversion_service import convert_to_pdf
from services.storage_service import upload_to_cloudinary
from services.openai_service import analyze_deck


def _run_analysis(deck_id: str, pdf_path: str):
    """Background thread: runs OpenAI analysis, uploads to Cloudinary, saves results."""
    deck = Deck.objects.get(id=deck_id)
    try:
        result = analyze_deck(pdf_path)
        pdf_url = upload_to_cloudinary(pdf_path, f'decks/{deck_id}')

        deck.pdf_url = pdf_url
        deck.startup_name = result.get('startup_name') or deck.startup_name
        deck.registered_name = result.get('registered_name', '')
        deck.website = result.get('website', '')
        deck.sector = result.get('sector', '')
        deck.sub_sector = result.get('sub_sector', '')
        deck.one_liner = result.get('one_liner', '')
        deck.founder_email_1 = result.get('founder_email_1', '')
        deck.founder_email_2 = result.get('founder_email_2', '')
        deck.founder_email_3 = result.get('founder_email_3', '')
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

        tmp_dir = Path('/tmp') if os.name != 'nt' else Path(os.environ.get('TEMP', 'C:/Temp'))
        tmp_dir.mkdir(exist_ok=True)
        tmp_path = tmp_dir / file.name
        with open(tmp_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

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
        threading.Thread(target=_run_analysis, args=(str(deck.id), pdf_path), daemon=True).start()
        return Response({'id': str(deck.id), 'status': 'processing'}, status=status.HTTP_202_ACCEPTED)
