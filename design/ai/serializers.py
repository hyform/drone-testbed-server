from rest_framework import serializers
from .models import Designer1, OpsPlan, UAVDesign, UAVDesign2, DroneBot, OpsService
import time
from .seqtosql.dronebotseqtosql import DroneBotSeqToSQL

class Designer1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Designer1
        fields = ['id', 'config', 'range', 'cost', 'payload', 'velocity']

class OpsPlanSerializer(serializers.Serializer):

    input = serializers.CharField(max_length=10000)
    output = serializers.CharField(required=False, allow_blank=True, max_length=10000)

    def create(self, validated_data):
        input = validated_data.get('input', 'Nothing')
        return OpsPlan(input)

class OpsServiceSerializer(serializers.Serializer):

    input = serializers.CharField(max_length=10000)

    startupCost = serializers.FloatField(required=False)
    total_weight_delivered = serializers.FloatField(required=False)
    total_food_delivered = serializers.FloatField(required=False)
    total_parcel_delivered = serializers.FloatField(required=False)
    operating_cost = serializers.FloatField(required=False)
    profit = serializers.FloatField(required=False)
    number_deliveries = serializers.FloatField(required=False)

    result = serializers.CharField(required=False, max_length=100)

    def create(self, validated_data):
        input = validated_data.get('input', 'Nothing')
        return OpsService(input)


class DroneBotSerializer(serializers.Serializer):

    input = serializers.CharField(max_length=10000)
    success = serializers.BooleanField()
    vehicles = serializers.SerializerMethodField()

    #DroneBot.initialize()  # maybe initial here on ppd and hyform

    def get_vehicles(self, obj):
        ret=[]
        result_vehicles = obj.vehicles
        for result in result_vehicles:
            vehicle_json = []
            if len(result)==5:
                vehicle_json.append({"config" : result[4]})
                # vehicle_json.append({"result" : result[1]})
                vehicle_json.append({"range" : result[0]})
                vehicle_json.append({"cost" : result[1]})
                vehicle_json.append({"capacity" : result[2]})
                vehicle_json.append({"velocity" : result[3]})
            ret.append(vehicle_json)
        return ret

    def create(self, validated_data):
        # DroneBot.initialize() # maybe initial here on local development project
        input = validated_data.get('input', 'Nothing')
        success = False
        print("the question: ", input)
        start_time = time.time()
        vehicles = DroneBotSeqToSQL.run(input)
        end_time = time.time()-start_time
        print('time to run seq2sql: ', end_time)
        if vehicles:
            success = True
        return DroneBot(input=input, success=success, vehicles=vehicles)


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
        t1 = time.time()
        ret=[]
        for traj in obj.trajs:
            dict={}
            dict['time']=traj.time
            dict['position']=[traj.x, traj.y, traj.z]
            dict['orientation']=[traj.rx, traj.ry, traj.rx, traj.rw]
            ret.append(dict)

        t2 = time.time()
        print("time to pack traj: ", t2-t1)
        return ret


    def create(self, validated_data):
        config = validated_data.get('config', 'Nothing')
        return UAVDesignTraj2(config)
