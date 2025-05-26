# # turbines/views.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework import viewsets
# from .services.mongo_service import MongoService
# from turbines.serializers import WindTurbineSerializer
# from .models import WindTurbine

# mongo_service = MongoService()

# class WindTurbineListCreateView(APIView):
#     def get(self, request):
#         turbines = mongo_service.list_wind_turbines()
#         serializer = WindTurbineSerializer(turbines, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = WindTurbineSerializer(data=request.data)
#         if serializer.is_valid():
#             turbine_id = mongo_service.insert_wind_turbine(serializer.validated_data)
#             return Response({"id": turbine_id}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class WindTurbineViewSet(viewsets.ViewSet):
#     queryset = WindTurbine.objects.all()
#     def list(self, request):
#         turbines = mongo_service.list_wind_turbines()
#         return Response(turbines)

#     def retrieve(self, request, pk=None):
#         turbine = mongo_service.get_wind_turbine(pk)
#         if turbine:
#             return Response(turbine)
#         return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
#     def create(self, request):
#         serializer = WindTurbineSerializer(data=request.data)
#         if serializer.is_valid():
#             turbine_id = mongo_service.insert_wind_turbine(serializer.validated_data)
#             return Response({'id': turbine_id}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def update(self, request, pk=None):
#         if mongo_service.update_wind_turbine(pk, request.data):
#             return Response({'detail': 'Updated'}, status=status.HTTP_200_OK)
#         return Response({'detail': 'Not found or not modified'}, status=status.HTTP_404_NOT_FOUND)
    
#     def destroy(self, request, pk=None):
#         if mongo_service.delete_wind_turbine(pk):
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


# def api_dashboard_view(request):
#     fields = ["name", "capacity_kw", "installation_date", "latitude", "longitude"]
#     fields_with_placeholders = [(f, f.replace('_', ' ').capitalize()) for f in fields]
#     return render(request, "dashboard.html", {"fields_with_placeholders": fields_with_placeholders})

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
