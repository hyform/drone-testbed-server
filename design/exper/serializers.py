from .models import Structure, Position, Session
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
