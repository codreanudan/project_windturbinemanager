from rest_framework import serializers
from .models import WindTurbine
from datetime import date

class WindTurbineSerializer(serializers.ModelSerializer):
    """Serializer for the WindTurbine model."""
    maintenance_overdue = serializers.SerializerMethodField()
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
