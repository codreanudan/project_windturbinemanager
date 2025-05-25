from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import render
from pathlib import Path

from .services.mongo_service import get_mongo_service
from .services.utils.mongo_adapter import drf_to_mongo, mongo_to_drf
from .serializers import MongoWindTurbineSerializer

BASE_DIR = Path(__file__).resolve().parent.parent

class MongoWindTurbineViewSet(viewsets.ViewSet):
    """
    API endpoint for wind turbines using MongoDB.
    """
    def list(self, request):
        # Pagination
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))
        mongo_service = get_mongo_service()
        turbines = mongo_service.list_turbines(limit=limit, offset=offset)
        count = mongo_service.count_turbines()
         # Convert to DRF format (convert date strings to date objects)
        turbines = [mongo_to_drf(t) for t in turbines]
        results = [MongoWindTurbineSerializer(t).data for t in turbines]
        return Response({"count": count, "results": results})

    def retrieve(self, request, pk=None):
        mongo_service = get_mongo_service()
        turbine = mongo_service.get_turbine(pk)
        if turbine:
            turbine = mongo_to_drf(turbine)
            return Response(MongoWindTurbineSerializer(turbine).data)
        return Response({'detail': 'Not found.'}, status=404)
    
    def create(self, request):
        mongo_service = get_mongo_service()
        data = drf_to_mongo(request.data)
        try:
            new_id = mongo_service.create_turbine(data)
            return Response({'id': new_id}, status=201)
        except Exception as e:
            return Response({'detail': str(e)}, status=400)

    def update(self, request, pk=None):
        mongo_service = get_mongo_service()
        data = drf_to_mongo(request.data)
        try:
            success = mongo_service.update_turbine(pk, data)
            if success:
                return Response({'id': pk})
            return Response({'detail': 'Update failed.'}, status=400)
        except Exception as e:
            return Response({'detail': str(e)}, status=400)

    def destroy(self, request, pk=None):
        mongo_service = get_mongo_service()
        try:
            success = mongo_service.delete_turbine(pk)
            if success:
                return Response(status=204)
            return Response({'detail': 'Delete failed.'}, status=400)
        except Exception as e:
            return Response({'detail': str(e)}, status=400)

def api_dashboard_view(request):
    fields = ["name", "capacity_kw", "installation_date", "latitude", "longitude"]
    fields_with_placeholders = [(f, f.replace('_', ' ').capitalize()) for f in fields]
    return render(request, "dashboard.html", {"fields_with_placeholders": fields_with_placeholders})