from django.shortcuts import render

from rest_framework import viewsets
from .models import WindTurbine
from .serializers import WindTurbineSerializer

from django.http import HttpResponse, Http404
from pathlib import Path
from django.conf import settings


BASE_DIR = Path(__file__).resolve().parent.parent
# Create your views here.

# This viewset automatically provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
class WindTurbineViewSet(viewsets.ModelViewSet):
    """
        API endpoint that allows wind turbines to be viewed or edited.
    """
    queryset = WindTurbine.objects.all()
    serializer_class = WindTurbineSerializer
    
def api_dashboard_view(request):
    return render(request, 'api_dashboard.html')
    

