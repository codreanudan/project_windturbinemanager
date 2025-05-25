# turbines/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewset with it
router = DefaultRouter()
router.register(r'turbines', views.WindTurbineViewSet, basename='windturbine')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]

# This will create the following URLs:
# /api/turbines/ - GET (list), POST (create)
# /api/turbines/{id}/ - GET (retrieve), PUT (update), PATCH (partial_update), DELETE (destroy)
# /api/turbines/maintenance_status/ - GET (custom action)