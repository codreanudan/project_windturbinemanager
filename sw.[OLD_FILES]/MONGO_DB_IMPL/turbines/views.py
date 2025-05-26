# views.py - Updated to work with MongoDB
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import WindTurbine  # Keep for serializer compatibility
from .serializers import WindTurbineSerializer, MongoWindTurbineSerializer
from .services.mongo_service import get_mongo_service
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent

class MongoWindTurbineViewSet(viewsets.ViewSet):
    """
    ViewSet for wind turbines using MongoDB backend
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mongo_service = get_mongo_service()
    
    def list(self, request):
        """List all wind turbines"""
        try:
            # Get query parameters
            limit = request.query_params.get('limit')
            offset = int(request.query_params.get('offset', 0))
            
            if limit:
                limit = int(limit)
            
            # Get filters from query params
            filters = {}
            if 'name' in request.query_params:
                filters['name'] = {'$regex': request.query_params['name'], '$options': 'i'}
            if 'maintenance_overdue' in request.query_params:
                if request.query_params['maintenance_overdue'].lower() == 'true':
                    filters['maintenance_done'] = False
            
            turbines = self.mongo_service.list_turbines(limit=limit, offset=offset, filters=filters)
            
            # Serialize the data
            serializer = MongoWindTurbineSerializer(turbines, many=True, context={'request': request})
            
            # Add pagination info
            total_count = self.mongo_service.count_turbines(filters)
            
            return Response({
                'count': total_count,
                'results': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error listing turbines: {e}")
            return Response(
                {'error': 'Failed to retrieve turbines'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request):
        """Create a new wind turbine"""
        try:
            serializer = MongoWindTurbineSerializer(data=request.data)
            
            if serializer.is_valid():
                # Create turbine in MongoDB
                turbine_id = self.mongo_service.create_turbine(serializer.validated_data)
                
                # Get the created turbine to return full data
                created_turbine = self.mongo_service.get_turbine(turbine_id)
                
                response_serializer = MongoWindTurbineSerializer(created_turbine, context={'request': request})
                
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating turbine: {e}")
            return Response(
                {'error': 'Failed to create turbine'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, pk=None):
        """Retrieve a specific wind turbine"""
        try:
            turbine = self.mongo_service.get_turbine(pk)
            
            if not turbine:
                return Response(
                    {'error': 'Turbine not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = MongoWindTurbineSerializer(turbine, context={'request': request})
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error retrieving turbine {pk}: {e}")
            return Response(
                {'error': 'Failed to retrieve turbine'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, pk=None):
        """Update a wind turbine"""
        try:
            # Check if turbine exists
            existing_turbine = self.mongo_service.get_turbine(pk)
            if not existing_turbine:
                return Response(
                    {'error': 'Turbine not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = MongoWindTurbineSerializer(data=request.data, partial=True)
            
            if serializer.is_valid():
                success = self.mongo_service.update_turbine(pk, serializer.validated_data)
                
                if success:
                    # Get updated turbine
                    updated_turbine = self.mongo_service.get_turbine(pk)
                    response_serializer = MongoWindTurbineSerializer(updated_turbine, context={'request': request})
                    return Response(response_serializer.data)
                else:
                    return Response(
                        {'error': 'No changes made'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating turbine {pk}: {e}")
            return Response(
                {'error': 'Failed to update turbine'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def partial_update(self, request, pk=None):
        """Partially update a wind turbine"""
        return self.update(request, pk)
    
    def destroy(self, request, pk=None):
        """Delete a wind turbine"""
        try:
            success = self.mongo_service.delete_turbine(pk)
            
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': 'Turbine not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            logger.error(f"Error deleting turbine {pk}: {e}")
            return Response(
                {'error': 'Failed to delete turbine'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def maintenance_overdue(self, request):
        """Get turbines that need maintenance"""
        try:
            turbines = self.mongo_service.get_maintenance_overdue()
            serializer = MongoWindTurbineSerializer(turbines, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting maintenance overdue turbines: {e}")
            return Response(
                {'error': 'Failed to retrieve maintenance data'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get turbines near a location"""
        try:
            lat = float(request.query_params.get('lat', 0))
            lon = float(request.query_params.get('lon', 0))
            radius = float(request.query_params.get('radius', 10))
            
            turbines = self.mongo_service.get_turbines_by_location(lat, lon, radius)
            serializer = MongoWindTurbineSerializer(turbines, many=True, context={'request': request})
            return Response(serializer.data)
            
        except (ValueError, TypeError) as e:
            return Response(
                {'error': 'Invalid coordinates or radius'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error getting nearby turbines: {e}")
            return Response(
                {'error': 'Failed to retrieve nearby turbines'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def health(self, request):
        """MongoDB health check"""
        try:
            health_info = self.mongo_service.health_check()
            return Response(health_info)
        except Exception as e:
            return Response(
                {'status': 'unhealthy', 'error': str(e)}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

# Keep the original viewset for backwards compatibility if needed
class WindTurbineViewSet(viewsets.ModelViewSet):
    """
    Original Django ORM-based API endpoint (kept for compatibility)
    """
    queryset = WindTurbine.objects.all()
    serializer_class = WindTurbineSerializer

def api_dashboard_view(request):
    """Dashboard view"""
    fields = ["name", "capacity_kw", "installation_date", "latitude", "longitude"]
    fields_with_placeholders = [(f, f.replace('_', ' ').capitalize()) for f in fields]
    return render(request, "dashboard.html", {"fields_with_placeholders": fields_with_placeholders})