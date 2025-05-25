# serializers.py
from rest_framework import serializers
from .models import WindTurbine
from datetime import date
from django.conf import settings
from .services.weather_service import WeatherAPIService
import math

OPENWEATHER_API_KEY = 'your_openweather_api_key_here'

class WindTurbineSerializer(serializers.ModelSerializer):
    """Serializer for the WindTurbine model, compatible with MongoDB."""
    
    # Handle both DRF 'id' and MongoDB '_id' formats
    id = serializers.CharField(read_only=True, required=False)
    
    # Computed fields
    maintenance_overdue = serializers.SerializerMethodField()
    wind_speed_kph = serializers.SerializerMethodField()
    instant_output_kw = serializers.SerializerMethodField()

    class Meta:
        model = WindTurbine
        fields = '__all__'
        read_only_fields = ('id',)

    def to_internal_value(self, data):
        """Handle incoming data, ensuring compatibility with MongoDB format"""
        # If data comes from MongoDB with '_id', convert to 'id'
        if '_id' in data and 'id' not in data:
            data = data.copy()
            data['id'] = data.pop('_id')
        
        return super().to_internal_value(data)

    def to_representation(self, instance):
        """Convert model instance to dictionary representation"""
        if isinstance(instance, dict):
            # Handle MongoDB document format
            data = instance.copy()
            
            # Ensure we have an 'id' field for DRF compatibility
            if '_id' in data and 'id' not in data:
                data['id'] = str(data.pop('_id'))
            elif 'id' in data and isinstance(data['id'], str):
                data['id'] = str(data['id'])
                
            # Add computed fields
            self._add_computed_fields(data)
            return data
        else:
            # Handle Django model instance
            return super().to_representation(instance)

    def _add_computed_fields(self, data):
        """Add computed fields to the data representation"""
        # Create a temporary object-like structure for method calls
        class TempObj:
            def __init__(self, data_dict):
                for key, value in data_dict.items():
                    setattr(self, key, value)
        
        temp_obj = TempObj(data)
        
        # Add computed fields
        data['maintenance_overdue'] = self.get_maintenance_overdue(temp_obj)
        data['wind_speed_kph'] = self.get_wind_speed_kph(temp_obj)
        data['instant_output_kw'] = self.get_instant_output_kw(temp_obj)

    def get_maintenance_overdue(self, obj):
        """Check if maintenance is overdue"""
        try:
            last_maintenance_date = getattr(obj, 'last_maintenance_date', None)
            maintenance_done = getattr(obj, 'maintenance_done', False)
            
            if not last_maintenance_date:
                return not maintenance_done
            
            if isinstance(last_maintenance_date, str):
                try:
                    from datetime import datetime
                    last_maintenance_date = datetime.fromisoformat(last_maintenance_date).date()
                except ValueError:
                    return not maintenance_done
            
            if date.today() > last_maintenance_date and not maintenance_done:
                return True
            return False
        except Exception:
            return False

    def get_wind_speed_kph(self, obj):
        """Get current wind speed for the turbine location"""
        try:
            latitude = getattr(obj, 'latitude', None)
            longitude = getattr(obj, 'longitude', None)
            
            if not latitude or not longitude:
                return None
                
            weather_service = WeatherAPIService("c67cac5327c741a7abb82828252505")
            data = weather_service.get_current_weather(latitude, longitude)
            return data.get("wind_kph")
        except Exception:
            return None

    def calculate_power_wind(self, v_kph: float, rotor_radius_m: float, cp: float = 0.4, air_density: float = 1.225) -> float:
        """Calculate theoretical power output based on wind speed"""
        v_ms = v_kph / 3.6
        area = math.pi * rotor_radius_m ** 2
        power_w = 0.5 * air_density * area * cp * (v_ms ** 3)
        return power_w

    def get_instant_output_kw(self, obj):
        """Calculate instant power output based on current wind conditions"""
        try:
            wind_speed = self.get_wind_speed_kph(obj)
            rotor_radius = 40
            capacity_kw = getattr(obj, 'capacity_kw', 0)
            
            if not wind_speed or wind_speed <= 0:
                return 0.0
                
            power_w = self.calculate_power_wind(wind_speed, rotor_radius)
            power_kw = power_w / 1000
            return min(int(power_kw), capacity_kw)
        except Exception:
            return 0.0