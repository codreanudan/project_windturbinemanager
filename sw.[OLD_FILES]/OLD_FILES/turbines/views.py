
from django.shortcuts import render
from rest_framework import viewsets
from .models import WindTurbine
from .serializers import WindTurbineSerializer
from pathlib import Path
from rest_framework.response import Response


BASE_DIR = Path(__file__).resolve().parent.parent

class WindTurbineViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows wind turbines to be viewed or edited.
    """
    queryset = WindTurbine.objects.all()
    serializer_class = WindTurbineSerializer

def api_dashboard_view(request):
    fields = ["name", "capacity_kw", "installation_date", "latitude", "longitude"]
    fields_with_placeholders = [(f, f.replace('_', ' ').capitalize()) for f in fields]
    return render(request, "dashboard.html", {"fields_with_placeholders": fields_with_placeholders})
