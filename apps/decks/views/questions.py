# Questions & email views: manage founder Q&A pairs and send selected questions via email.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.decks.models import Deck
from services.email_service import send_founder_questions


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

        normalised = [
            {'question': str(item.get('question', '')), 'answer': str(item.get('answer', ''))}
            for item in questions if isinstance(item, dict)
        ]
        deck.founder_questions = normalised
        deck.save(update_fields=['founder_questions'])
        return Response({'founder_questions': deck.founder_questions})


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

        selected_indices = request.data.get('selected_indices')
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

        emailed = set(deck.emailed_questions or [])
        emailed.update(selected_indices)
        deck.emailed_questions = sorted(emailed)
        deck.save(update_fields=['emailed_questions'])
        return Response({'message': 'Email sent successfully.', 'emailed_questions': deck.emailed_questions})
