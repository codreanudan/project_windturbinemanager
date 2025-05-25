# serializers.py - Updated with MongoDB-compatible serializer
from rest_framework import serializers
from .models import WindTurbine
from datetime import date, datetime, timedelta
from django.conf import settings
from .services.weather_service import WeatherAPIService
import math
import logging

logger = logging.getLogger(__name__)

class MongoWindTurbineSerializer(serializers.Serializer):
    """MongoDB-compatible serializer for WindTurbine data"""
    
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=100)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    installation_date = serializers.DateField()
    capacity_kw = serializers.FloatField(help_text="Puterea instalată în kW")
    
    # Maintenance fields
    last_maintenance_date = serializers.DateField(required=False, allow_null=True)
    maintenance_done = serializers.BooleanField(default=False)
    
    # Output field
    instant_output_kw = serializers.FloatField(default=0.0, read_only=True)
    
    # Computed fields
    maintenance_overdue = serializers.SerializerMethodField()
    wind_speed_kph = serializers.SerializerMethodField()
    
    def validate_name(self, value):
        """Validate turbine name is unique"""
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        return value.strip()
    
    def validate_latitude(self, value):
        """Validate latitude is within valid range"""
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value
    
    def validate_longitude(self, value):
        """Validate longitude is within valid range"""
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value
    
    def validate_capacity_kw(self, value):
        """Validate capacity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Capacity must be greater than 0")
        return value
    
    def validate_installation_date(self, value):
        """Validate installation date is not in the future"""
        if value > date.today():
            raise serializers.ValidationError("Installation date cannot be in the future")
        return value
    
    def validate_last_maintenance_date(self, value):
        """Validate maintenance date"""
        if value and value > date.today():
            raise serializers.ValidationError("Maintenance date cannot be in the future")
        return value
    
    def get_maintenance_overdue(self, obj):
        """Check if maintenance is overdue"""
        try:
            # If maintenance is explicitly marked as not done
            if not obj.get('maintenance_done', False):
                return True
            
            # If no maintenance date is set
            last_maintenance = obj.get('last_maintenance_date')
            if not last_maintenance:
                return True
            
            # Convert to date if it's a datetime
            if isinstance(last_maintenance, datetime):
                last_maintenance = last_maintenance.date()
            
            # Check if more than 7 days since last maintenance
            if isinstance(last_maintenance, date):
                days_since = (date.today() - last_maintenance).days
                return days_since > 7
            
            return False
            
        except Exception as e:
            logger.warning(f"Error calculating maintenance overdue: {e}")
            return False
    
    def get_wind_speed_kph(self, obj):
        """Get current wind speed from weather API"""
        try:
            if not hasattr(self, '_weather_service'):
                # Cache weather service instance
                api_key = 'c67cac5327c741a7abb82828252505'
                self._weather_service = WeatherAPIService(api_key)
            
            latitude = obj.get('latitude')
            longitude = obj.get('longitude')
            
            if latitude is None or longitude is None:
                return None
            
            data = self._weather_service.get_current_weather(latitude, longitude)
            return data.get("wind_kph") if data else None
            
        except Exception as e:
            logger.warning(f"Error getting wind speed for turbine {obj.get('name', 'Unknown')}: {e}")
            return None
    
    def calculate_power_from_wind(self, wind_speed_kph: float, rotor_radius_m: float = 40, 
                                  cp: float = 0.4, air_density: float = 1.225) -> float:
        """Calculate theoretical power output from wind speed"""
        try:
            # Convert wind speed from km/h to m/s
            wind_speed_ms = wind_speed_kph / 3.6
            
            # Calculate swept area
            swept_area = math.pi * rotor_radius_m ** 2
            
            # Calculate power using wind power formula: P = 0.5 * ρ * A * Cp * v³
            power_watts = 0.5 * air_density * swept_area * cp * (wind_speed_ms ** 3)
            
            # Convert to kW
            power_kw = power_watts / 1000
            
            return power_kw
            
        except Exception as e:
            logger.warning(f"Error calculating power from wind: {e}")
            return 0.0
    
    def get_instant_output_kw(self, obj):
        """Calculate instant power output based on current wind conditions"""
        try:
            wind_speed = self.get_wind_speed_kph(obj)
            
            if not wind_speed or wind_speed <= 0:
                return 0.0
            
            # Calculate theoretical power
            theoretical_power = self.calculate_power_from_wind(wind_speed)
            
            # Cap at turbine capacity
            capacity = obj.get('capacity_kw', 0)
            actual_power = min(theoretical_power, capacity)
            
            # Round to reasonable precision
            return round(actual_power, 2)
            
        except Exception as e:
            logger.warning(f"Error calculating instant output: {e}")
            return 0.0
    
    def to_representation(self, instance):
        """Customize the representation of the data"""
        data = super().to_representation(instance)
        
        # Ensure consistent data types
        if data.get('instant_output_kw'):
            data['instant_output_kw'] = float(data['instant_output_kw'])
        
        # Add computed fields that depend on real-time data
        if hasattr(self, 'context') and self.context.get('include_realtime', True):
            data['wind_speed_kph'] = self.get_wind_speed_kph(instance)
            data['instant_output_kw'] = self.get_instant_output_kw(instance)
        
        return data

# Keep original serializer for backwards compatibility
class WindTurbineSerializer(serializers.ModelSerializer):
    """Original Django ORM-based serializer (kept for compatibility)"""
    
    id = serializers.CharField(read_only=True)
    maintenance_overdue = serializers.SerializerMethodField()
    wind_speed_kph = serializers.SerializerMethodField()
    instant_output_kw = serializers.SerializerMethodField()

    class Meta:
        model = WindTurbine
        fields = '__all__'
        read_only_fields = ('id',)
    
    def get_maintenance_overdue(self, obj):
        if not obj.last_maintenance_date:
            return False  
        if date.today() > obj.last_maintenance_date and not obj.maintenance_done:
            return True
        return False
    
    def get_wind_speed_kph(self, obj):  
        try:
            weather_service = WeatherAPIService("c67cac5327c741a7abb82828252505")
            data = weather_service.get_current_weather(obj.latitude, obj.longitude)
            return data.get("wind_kph")
        except Exception as e:
            return None

    def calculate_power_wind(self, v_kph: float, rotor_radius_m: float, cp: float = 0.4, air_density: float = 1.225) -> float:
        v_ms = v_kph / 3.6
        area = math.pi * rotor_radius_m ** 2
        power_w = 0.5 * air_density * area * cp * (v_ms ** 3)
        return power_w

    def get_instant_output_kw(self, obj):
        wind_speed = self.get_wind_speed_kph(obj)
        rotor_radius = 40  
        if not wind_speed:
            return 0.0
        power_w = self.calculate_power_wind(wind_speed, rotor_radius)
        power_kw = power_w / 1000
        return min(int(power_kw), obj.capacity_kw)