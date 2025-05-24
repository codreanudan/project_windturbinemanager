from rest_framework import serializers
from .models import WindTurbine

class WindTurbineSerializer(serializers.ModelSerializer):
    """Serializer for the WindTurbine model."""
    class Meta:
        """Meta class for the WindTurbineSerializer."""
        model = WindTurbine
        fields = '__all__'