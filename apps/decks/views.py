# Deck views: upload pipeline, list with filtering, detail, email, CRM status update, and comments.

import os
import threading
from pathlib import Path

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser

from .models import Deck, Comment
from .serializers import DeckListSerializer, DeckDetailSerializer, CommentSerializer, FounderContactSerializer
from apps.setup.models import FirmPreferences
from services.conversion_service import convert_to_pdf
from services.storage_service import upload_to_cloudinary
from services.openai_service import analyze_deck
from services.email_service import send_founder_questions


def _run_analysis(deck_id: str, pdf_path: str):
    """Background thread: runs OpenAI analysis, uploads to Cloudinary, saves results."""
    from .models import Deck
    deck = Deck.objects.get(id=deck_id)
    try:
        prefs = FirmPreferences.objects.first()
        result = analyze_deck(pdf_path, prefs)
        pdf_url = upload_to_cloudinary(pdf_path, f'decks/{deck_id}')

        deck.pdf_url = pdf_url
        deck.startup_name = result.get('startup_name') or deck.startup_name
        deck.sector = result.get('sector', '')
        deck.founder_email = result.get('founder_email', '')
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
        qs = Deck.objects.all()
        sector = request.query_params.get('sector')
        crm_status = request.query_params.get('crm_status')
        if sector:
            qs = qs.filter(sector__icontains=sector)
        if crm_status:
            qs = qs.filter(crm_status=crm_status)
        return Response(DeckListSerializer(qs, many=True).data)


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


class DeckCrmStatusView(APIView):
    def patch(self, request, pk):
        """Update only the CRM status (Pending / Approved / Rejected)."""
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

        # Support sending only selected questions (list of indices)
        selected_indices = request.data.get('selected_indices', None)
        if selected_indices is not None:
            questions = [
                deck.founder_questions[i]['question']
                for i in selected_indices
                if 0 <= i < len(deck.founder_questions)
            ]
        else:
            questions = [q['question'] for q in deck.founder_questions]
            selected_indices = list(range(len(deck.founder_questions)))

        if not questions:
            return Response({'error': 'No questions selected.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            send_founder_questions(recipient, deck.startup_name, questions)
        except Exception as e:
            return Response({'error': f'Email failed: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Merge newly emailed indices into emailed_questions
        emailed = set(deck.emailed_questions or [])
        emailed.update(selected_indices)
        deck.emailed_questions = sorted(emailed)
        deck.save(update_fields=['emailed_questions'])

        return Response({'message': 'Email sent successfully.', 'emailed_questions': deck.emailed_questions})


class CallNotesView(APIView):
    SECTIONS = [
        'overview', 'problem', 'solution', 'product_business_model',
        'traction_metrics', 'founding_team', 'competition',
        'roadmap_gtm', 'fundraise_history',
    ]

    def patch(self, request, pk):
        """Save call notes. Accepts partial dict — only provided keys are updated."""
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)

        notes = request.data.get('call_notes', {})
        if not isinstance(notes, dict):
            return Response({'error': 'call_notes must be an object.'}, status=status.HTTP_400_BAD_REQUEST)

        current = deck.call_notes or {}
        current.update({k: v for k, v in notes.items() if k in self.SECTIONS})
        deck.call_notes = current
        deck.save(update_fields=['call_notes'])
        return Response({'call_notes': deck.call_notes})


class QuestionsView(APIView):
    def patch(self, request, pk):
        """Replace the full founder_questions array. Each item: {question, answer}."""
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)

        questions = request.data.get('founder_questions')
        if not isinstance(questions, list):
            return Response({'error': 'founder_questions must be a list.'}, status=status.HTTP_400_BAD_REQUEST)

        # Normalise — ensure each item has question + answer keys
        normalised = []
        for item in questions:
            if isinstance(item, dict):
                normalised.append({'question': str(item.get('question', '')), 'answer': str(item.get('answer', ''))})
        deck.founder_questions = normalised
        deck.save(update_fields=['founder_questions'])
        return Response({'founder_questions': deck.founder_questions})


class FounderContactView(APIView):
    def patch(self, request, pk):
        """Update founder name, email, and LinkedIn for a deck."""
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FounderContactSerializer(deck, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)


class CommentListView(APIView):
    def get(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CommentSerializer(deck.comments.all(), many=True).data)

    def post(self, request, pk):
        try:
            deck = Deck.objects.get(id=pk)
        except Deck.DoesNotExist:
            return Response({'error': 'Deck not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(deck=deck, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDeleteView(APIView):
    def delete(self, request, pk, comment_id):
        try:
            comment = Comment.objects.get(id=comment_id, deck_id=pk)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)
        if comment.author != request.user:
            return Response({'error': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
