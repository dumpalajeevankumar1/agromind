from rest_framework import serializers
from .models import SensorReading, ChatLog

class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = 'id', 'timestamp', 'temperature', 'humidity', 'soil_moisture', 'ph_value'
        extra_kwargs = {
            'ph_value': {'required': False, 'allow_null': True}
        }

class ChatLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatLog
        fields = "__all__"
        


