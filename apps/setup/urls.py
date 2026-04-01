# URL route for firm preferences: single endpoint handles both GET and PUT.

from django.urls import path
from .views import FirmPreferencesView

urlpatterns = [
    path('', FirmPreferencesView.as_view(), name='firm-preferences'),
]
