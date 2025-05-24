from django.db import models

# Create your models here.

class WindTurbine(models.Model):
    """Model representing a wind turbine."""
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    installation_date = models.DateField()
    capacity_kw = models.FloatField(help_text="Puterea instalată în kW")
    
    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"