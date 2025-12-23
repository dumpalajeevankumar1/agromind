from django.contrib import admin
from .models import FarmerProfile, EquipmentData, ChatLog, SensorReading

admin.site.register(FarmerProfile)
admin.site.register(EquipmentData)
admin.site.register(ChatLog)
@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'temperature', 'humidity', 'soil_moisture', 'ph_value')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)
