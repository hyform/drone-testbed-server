from rest_framework import serializers
from .models import Designer1, OpsPlan1, UAVDesign, UAVDesign2, UAVDesignTraj2

class Designer1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Designer1
        fields = ['id', 'config', 'range', 'cost', 'payload']


class OpsPlan1Serializer(serializers.Serializer):
    input = serializers.CharField(max_length=10000)
    output = serializers.CharField(required=False, allow_blank=True, max_length=10000)

    def create(self, validated_data):
        input = validated_data.get('input', 'Nothing')
        # output = input + ' some output'
        return OpsPlan1(input)

class UAVDesignSerializer(serializers.Serializer):
    config = serializers.CharField(max_length=1000)
    result = serializers.CharField(required=False, allow_blank=True, max_length=100)
    range = serializers.FloatField(required=False)
    velocity = serializers.FloatField(required=False)
    cost = serializers.FloatField(required=False)

    def create(self, validated_data):
        config = validated_data.get('config', 'Nothing')
        return UAVDesign(config)

class UAVDesign2Serializer(serializers.Serializer):
    config = serializers.CharField(max_length=1000)
    result = serializers.CharField(required=False, allow_blank=True, max_length=100)
    range = serializers.FloatField(required=False)
    velocity = serializers.FloatField(required=False)
    cost = serializers.FloatField(required=False)

    def create(self, validated_data):
        config = validated_data.get('config', 'Nothing')
        return UAVDesign2(config)


class UAVDesign2TrajSerializer(serializers.Serializer):
    config = serializers.CharField(max_length=1000)
    result = serializers.CharField(required=False, allow_blank=True, max_length=100)
    range = serializers.FloatField(required=False)
    velocity = serializers.FloatField(required=False)
    cost = serializers.FloatField(required=False)
    trajectory = serializers.SerializerMethodField()

    def get_trajectory(self, obj):
        ret=[]
        for traj in obj.trajs:
            dict={}
            dict['time']=traj.time
            dict['position']=[traj.x, traj.y, traj.z]
            dict['orientation']=[traj.rx, traj.ry, traj.rx, traj.rw]
            ret.append(dict)
        return ret


    def create(self, validated_data):
        config = validated_data.get('config', 'Nothing')
        return UAVDesignTraj2(config)
