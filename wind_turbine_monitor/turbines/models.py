from django.db import models
from django.utils import timezone

class WindTurbine(models.Model):
    """Model representing a wind turbine."""
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    installation_date = models.DateField()
    capacity_kw = models.FloatField(help_text="Puterea instalată în kW")
    
    # Câmpuri mentenanță
    last_maintenance_date = models.DateField(null=True, blank=True)
    maintenance_done = models.BooleanField(default=False)
    
    # Exemplu output instantaneu (putere instantanee)
    instant_output_kw = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"
    
    def maintenance_overdue(self):
        """
        Returns True if maintenance is overdue.
        Maintenance is considered overdue if:
        - Maintenance has not been done yet.
        - Last maintenance date is not set.
        """
        if not self.maintenance_done:
            return True
        if not self.last_maintenance_date:
            return True
        # Dacă ultima revizie a fost făcută cu mai mult de X zile în urmă (de exemplu, 365 zile)
        return (timezone.now().date() - self.last_maintenance_date).days > 7
