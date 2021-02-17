from .models import Structure, Position, Session, DigitalTwin
from rest_framework import serializers

class StructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Structure
        fields = ['id', 'name']

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name']

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

class DigitalTwinSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalTwin
        fields = ['open_time_interval', 'save_time_interval', 'quality_bias', 'self_bias', 'temperature', 'satisficing_factor']
