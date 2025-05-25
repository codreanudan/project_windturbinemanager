from rest_framework import serializers
from .models import WindTurbine
from datetime import date
from django.conf import settings
from .services.weather_service import WeatherAPIService
import math

OPENWEATHER_API_KEY = 'your_openweather_api_key_here'  

class WindTurbineSerializer(serializers.ModelSerializer):
    """Serializer for the WindTurbine model."""
    id = serializers.CharField(read_only=True)
    maintenance_overdue = serializers.SerializerMethodField()
    wind_speed_kph = serializers.SerializerMethodField()
    instant_output_kw = serializers.SerializerMethodField()

    class Meta:
        """Meta class for the WindTurbineSerializer."""
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

