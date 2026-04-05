# URL routes for deck operations: list, upload, detail, email, and comments endpoints.

from django.urls import path
from .views import DeckListView, DeckUploadView, DeckDetailView, DeckEmailView, CommentListView, CommentDeleteView

urlpatterns = [
    path('', DeckListView.as_view(), name='deck-list'),
    path('upload/', DeckUploadView.as_view(), name='deck-upload'),
    path('<uuid:pk>/', DeckDetailView.as_view(), name='deck-detail'),
    path('<uuid:pk>/email/', DeckEmailView.as_view(), name='deck-email'),
    path('<uuid:pk>/comments/', CommentListView.as_view(), name='deck-comments'),
    path('<uuid:pk>/comments/<uuid:comment_id>/', CommentDeleteView.as_view(), name='deck-comment-delete'),
]
