# URL routes for all deck operations including CRM status update.

from django.urls import path
from .views import (
    DeckListView, DeckUploadView, DeckDetailView, DeckBulkDeleteView,
    DeckEmailView, DeckCrmStatusView, FounderContactView, QuestionsView,
    CallNotesView, CommentListView, CommentDeleteView,
)

urlpatterns = [
    path('', DeckListView.as_view(), name='deck-list'),
    path('upload/', DeckUploadView.as_view(), name='deck-upload'),
    path('bulk-delete/', DeckBulkDeleteView.as_view(), name='deck-bulk-delete'),
    path('<uuid:pk>/', DeckDetailView.as_view(), name='deck-detail'),
    path('<uuid:pk>/email/', DeckEmailView.as_view(), name='deck-email'),
    path('<uuid:pk>/crm-status/', DeckCrmStatusView.as_view(), name='deck-crm-status'),
    path('<uuid:pk>/founder/', FounderContactView.as_view(), name='deck-founder'),
    path('<uuid:pk>/questions/', QuestionsView.as_view(), name='deck-questions'),
    path('<uuid:pk>/call-notes/', CallNotesView.as_view(), name='deck-call-notes'),
    path('<uuid:pk>/comments/', CommentListView.as_view(), name='deck-comments'),
    path('<uuid:pk>/comments/<uuid:comment_id>/', CommentDeleteView.as_view(), name='deck-comment-delete'),
]
