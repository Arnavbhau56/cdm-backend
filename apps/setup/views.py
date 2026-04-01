# Setup views: GET returns the single FirmPreferences row; PUT updates it in place.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import FirmPreferences
from .serializers import FirmPreferencesSerializer


class FirmPreferencesView(APIView):
    def _get_prefs(self):
        prefs, _ = FirmPreferences.objects.get_or_create(pk=1)
        return prefs

    def get(self, request):
        return Response(FirmPreferencesSerializer(self._get_prefs()).data)

    def put(self, request):
        prefs = self._get_prefs()
        serializer = FirmPreferencesSerializer(prefs, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data)
