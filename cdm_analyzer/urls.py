# Root URL configuration — routes all API traffic to the correct app routers.

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.auth_app.urls')),
    path('api/decks/', include('apps.decks.urls')),
    path('api/setup/', include('apps.setup.urls')),
]
