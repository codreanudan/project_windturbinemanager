# views.py
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import WindTurbine
from .serializers import WindTurbineSerializer
from .services.mongo_service import MongoService
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent

class WindTurbineViewSet(viewsets.ViewSet):
    """
    ViewSet that uses MongoDB for data storage while maintaining DRF compatibility.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mongo_service = MongoService()
        self.mongo_service.init_mongo_connection()

    def list(self, request):
        """List all wind turbines"""
        try:
            # Get pagination parameters
            limit = request.query_params.get('limit')
            offset = int(request.query_params.get('offset', 0))
            
            if limit:
                limit = int(limit)
            
            turbines = self.mongo_service.list_wind_turbines(limit=limit, offset=offset)
            serializer = WindTurbineSerializer(turbines, many=True)
            
            # Add pagination info if requested
            response_data = serializer.data
            if limit:
                total_count = self.mongo_service.count_wind_turbines()
                response_data = {
                    'count': total_count,
                    'results': serializer.data
                }
            
            return Response(response_data)
        except Exception as e:
            logger.error(f"Error listing turbines: {e}")
            return Response(
                {'error': 'Failed to retrieve turbines'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """Retrieve a specific wind turbine"""
        try:
            turbine = self.mongo_service.get_wind_turbine(pk)
            if turbine:
                serializer = WindTurbineSerializer(turbine)
                return Response(serializer.data)
            return Response(
                {'detail': 'Wind turbine not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving turbine {pk}: {e}")
            return Response(
                {'error': 'Failed to retrieve turbine'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request):
        """Create a new wind turbine"""
        try:
            serializer = WindTurbineSerializer(data=request.data)
            if serializer.is_valid():
                turbine_id = self.mongo_service.insert_wind_turbine(serializer.validated_data)
                
                # Return the created turbine with its new ID
                created_turbine = self.mongo_service.get_wind_turbine(turbine_id)
                response_serializer = WindTurbineSerializer(created_turbine)
                
                return Response(
                    response_serializer.data, 
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating turbine: {e}")
            return Response(
                {'error': 'Failed to create turbine'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        """Update a wind turbine (PUT)"""
        try:
            serializer = WindTurbineSerializer(data=request.data)
            if serializer.is_valid():
                success = self.mongo_service.update_wind_turbine(pk, serializer.validated_data)
                if success:
                    updated_turbine = self.mongo_service.get_wind_turbine(pk)
                    response_serializer = WindTurbineSerializer(updated_turbine)
                    return Response(response_serializer.data)
                return Response(
                    {'detail': 'Wind turbine not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating turbine {pk}: {e}")
            return Response(
                {'error': 'Failed to update turbine'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def partial_update(self, request, pk=None):
        """Partially update a wind turbine (PATCH)"""
        try:
            # Get existing turbine for partial update
            existing_turbine = self.mongo_service.get_wind_turbine(pk)
            if not existing_turbine:
                return Response(
                    {'detail': 'Wind turbine not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = WindTurbineSerializer(
                existing_turbine, 
                data=request.data, 
                partial=True
            )
            if serializer.is_valid():
                success = self.mongo_service.update_wind_turbine(pk, serializer.validated_data)
                if success:
                    updated_turbine = self.mongo_service.get_wind_turbine(pk)
                    response_serializer = WindTurbineSerializer(updated_turbine)
                    return Response(response_serializer.data)
                return Response(
                    {'detail': 'Failed to update turbine'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error partially updating turbine {pk}: {e}")
            return Response(
                {'error': 'Failed to update turbine'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, pk=None):
        """Delete a wind turbine"""
        try:
            success = self.mongo_service.delete_wind_turbine(pk)
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'Wind turbine not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error deleting turbine {pk}: {e}")
            return Response(
                {'error': 'Failed to delete turbine'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def maintenance_status(self, request):
        """Get maintenance status for all turbines"""
        try:
            turbines = self.mongo_service.list_wind_turbines()
            overdue_turbines = []
            
            for turbine in turbines:
                serializer = WindTurbineSerializer(turbine)
                turbine_data = serializer.data
                if turbine_data.get('maintenance_overdue', False):
                    overdue_turbines.append(turbine_data)
            
            return Response({
                'total_turbines': len(turbines),
                'overdue_maintenance': len(overdue_turbines),
                'overdue_turbines': overdue_turbines
            })
        except Exception as e:
            logger.error(f"Error getting maintenance status: {e}")
            return Response(
                {'error': 'Failed to get maintenance status'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def api_dashboard_view(request):
    """Render the API dashboard"""
    fields = ["name", "capacity_kw", "installation_date", "latitude", "longitude"]
    fields_with_placeholders = [(f, f.replace('_', ' ').capitalize()) for f in fields]
    return render(request, "dashboard.html", {"fields_with_placeholders": fields_with_placeholders})