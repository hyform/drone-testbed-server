from django.contrib.auth.models import User
from rest_framework import serializers
from chat.models import Message, Channel, ChannelPosition
from exper.serializers import StructureSerializer, PositionSerializer

class ChannelSerializer(serializers.ModelSerializer):
    structure = StructureSerializer(read_only=True)

    class Meta:
        model = Channel
        fields = ['id', 'name', 'structure']

class ChannelPositionSerializer(serializers.ModelSerializer):
    channel = ChannelSerializer(read_only=True)
    position = PositionSerializer(read_only=True) 
   
    class Meta:
        model = ChannelPosition
        fields = ['id', 'channel', 'position'] 
