from django.urls import path
from .views import FirmPreferencesView, PromptListView, PromptDetailView

urlpatterns = [
    path('', FirmPreferencesView.as_view(), name='firm-preferences'),
    path('prompts/', PromptListView.as_view(), name='prompt-list'),
    path('prompts/<int:pk>/', PromptDetailView.as_view(), name='prompt-detail'),
]
