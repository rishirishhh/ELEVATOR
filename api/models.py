from django.db import models

# Create your models here.
class Elevator(models.Model):
    current_floor = models.PositiveIntegerField(default=1)
    door_opened = models.BooleanField(default=False)
    in_maintenance = models.BooleanField(default=False)
    direction = models.IntegerField(default=0)

    def __str__(self):
        return f"Elevator {self.pk}" 
    
class Request(models.Model):
    elevator = models.ForeignKey(Elevator, on_delete=models.CASCADE, related_name='requests')
    is_complete = models.BooleanField(default=False)
    requested_from_floor = models.PositiveIntegerField(blank=True, null=True)
    requested_to_floor = models.PositiveIntegerField(blank=True, null=True)
    current_floor = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request {self.pk} for Elevator {self.elevator.pk}" 