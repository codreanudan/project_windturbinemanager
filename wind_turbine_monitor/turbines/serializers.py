from rest_framework import serializers
from .services.weather_service import WeatherAPIService
from datetime import date
import math

class MongoWindTurbineSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    installation_date = serializers.DateField()
    capacity_kw = serializers.FloatField()
    last_maintenance_date = serializers.DateField(allow_null=True, required=False)
    maintenance_done = serializers.BooleanField(default=False)

    maintenance_overdue = serializers.SerializerMethodField()
    wind_speed_kph = serializers.SerializerMethodField()
    instant_output_kw = serializers.SerializerMethodField()

    def get_maintenance_overdue(self, obj):
        from datetime import date, datetime

        last_maintenance = obj.get('last_maintenance_date')
        if not last_maintenance:
            return False

        # Convert string to date if needed
        if isinstance(last_maintenance, str):
            try:
                last_maintenance = datetime.fromisoformat(last_maintenance).date()
            except Exception:
                return False

        if date.today() > last_maintenance and not obj.get('maintenance_done', False):
            return True
        return False

    def get_wind_speed_kph(self, obj):
        print("Serializer: get_wind_speed_kph called for", obj.get('name'), obj.get('latitude'), obj.get('longitude'))
        try:
            weather_service = WeatherAPIService(api_key='c67cac5327c741a7abb82828252505')
            data = weather_service.get_current_weather(obj['latitude'], obj['longitude'])
            return data.get("wind_kph")
        except Exception:
            return None

    def calculate_power_wind(self, v_kph: float, rotor_radius_m: float, cp: float = 0.4, air_density: float = 1.225) -> float:
        v_ms = v_kph / 3.6
        area = math.pi * rotor_radius_m ** 2
        power_w = 0.5 * air_density * area * cp * (v_ms ** 3)  * 10
        return power_w

    def get_instant_output_kw(self, obj):
        wind_speed = self.get_wind_speed_kph(obj)
        rotor_radius = 40
        if not wind_speed:
            return 0.0
        power_w = self.calculate_power_wind(wind_speed, rotor_radius)
        power_kw = power_w / 1000
        return min(int(power_kw), obj['capacity_kw'])