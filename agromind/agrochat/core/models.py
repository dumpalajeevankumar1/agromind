from django.db import models
from django.contrib.auth.models import User

class ChatLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_logs")
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.question[:50]}"


# ------------------------------------------
# Equipment Data Model
# ------------------------------------------
class EquipmentData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="equipment_data")
    soil_moisture = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"


# ------------------------------------------
# Farmer Profile Model
# ------------------------------------------
class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    farm_name = models.CharField(max_length=100, blank=True, null=True)
    farm_location = models.CharField(max_length=200)
    farm_size = models.CharField(
        max_length=20,
        choices=[
            ('small', 'Small (< 5 acres)'),
            ('medium', 'Medium (5–20 acres)'),
            ('large', 'Large (> 20 acres)'),
        ],
    )
    crop_type = models.CharField(max_length=50)
    notifications = models.BooleanField(default=True)
    language = models.CharField(max_length=20, default='English')

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"
    


class SensorReading(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    soil_moisture = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    ph_value = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reading {self.id} - {self.timestamp}"
