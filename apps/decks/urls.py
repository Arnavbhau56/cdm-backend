# URL routes for deck operations: list, upload, detail, and email endpoints.

from django.urls import path
from .views import DeckListView, DeckUploadView, DeckDetailView, DeckEmailView

urlpatterns = [
    path('', DeckListView.as_view(), name='deck-list'),
    path('upload/', DeckUploadView.as_view(), name='deck-upload'),
    path('<uuid:pk>/', DeckDetailView.as_view(), name='deck-detail'),
    path('<uuid:pk>/email/', DeckEmailView.as_view(), name='deck-email'),
]
