from django.contrib.auth.models import User
from rest_framework import serializers
from repo.models import DesignTeam, Profile, Vehicle, Address, Customer, CustomerScenario, Warehouse, Scenario, Waypoint, Path, PathCustomer, Plan, DataLog
from repo.models import VehicleDemo, ScenarioDemo, OpsPlanDemo, PlayDemo
from exper.models import Group, Session


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignTeam
        fields = ['id', 'name', 'initialscore', 'currentscore']

class ProfileSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class  Meta:
        model = Profile
        fields = ['team']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'profile']


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'tag', 'config', 'result', 'range', 'velocity', 'cost', 'payload']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'x', 'z', 'region']


class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    address_id = serializers.PrimaryKeyRelatedField(source='address', write_only=True, queryset=Address.objects.all())

    class Meta:
        model = Customer
        fields = ['id', 'address', 'address_id', 'market', 'payload', 'weight' ]

class WarehouseSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    address_id = serializers.PrimaryKeyRelatedField(source='address', write_only=True, queryset=Address.objects.all())

    class Meta:
        model = Warehouse
        fields = ['id', 'address', 'address_id']

class ScenarioSerializer(serializers.ModelSerializer):
    customers = serializers.SerializerMethodField()
    warehouse = WarehouseSerializer(read_only=True)

    def get_customers(self, obj):
        # cs = CustomerScenario.objects.filter(scenario=obj)
        ret=[]
        for c in CustomerScenario.objects.filter(scenario=obj).iterator():
            customer = c.customer
            cs_dict={}
            cs_dict['id']=customer.id
            cs_dict['address']=AddressSerializer(customer.address).data
            cs_dict['market']=customer.market.id
            cs_dict['payload']=customer.payload
            cs_dict['weight']=customer.weight
            # cs_dict = CustomerSerializer(c.customer).data
            cs_dict['selected'] =  c.selected
            ret.append(cs_dict)
        return ret


    class Meta:
        model = Scenario
        fields = ['id', 'tag', 'version', 'warehouse', 'customers']

class Scenario2Serializer(serializers.Serializer):
    id = serializers.IntegerField()
    tag = serializers.CharField(max_length=100)
    version = serializers.IntegerField()
    warehouse = WarehouseSerializer(read_only=True)
    customers = serializers.SerializerMethodField()

    def get_customers(self, obj):
        # cs = CustomerScenario.objects.filter(scenario=obj)
        ret=[]
        for c in CustomerScenario.objects.filter(scenario=obj).iterator():
            customer = c.customer
            cs_dict={}
            cs_dict['id']=customer.id
            cs_dict['address']=AddressSerializer(customer.address).data
            cs_dict['market']=customer.market.id
            cs_dict['payload']=customer.payload
            cs_dict['weight']=customer.weight
            # cs_dict = CustomerSerializer(c.customer).data
            cs_dict['selected'] =  c.selected
            ret.append(cs_dict)
        return ret


class WaypointSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(source='customer', write_only=True, queryset=Customer.objects.all())

    class Meta:
        model = Waypoint
        fields = ['id', 'customer', 'customer_id', 'deliverytime']

class PathSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.PrimaryKeyRelatedField(source='vehicle', write_only=True, queryset=Vehicle.objects.all())
    warehouse = WarehouseSerializer(read_only=True)
    warehouse_id = serializers.PrimaryKeyRelatedField(source='warehouse', write_only=True, queryset=Warehouse.objects.all())
    # customers = CustomerSerializer(many=True, read_only=True)
    # customer_ids = serializers.PrimaryKeyRelatedField(source='customers', many=True, write_only=True, queryset=Customer.objects.all())
    customers = serializers.SerializerMethodField()


    def get_customers(self, obj):
        # pc = PathCustomer.objects.filter(path=obj).order_by('stop')
        ret = []
        for c in PathCustomer.objects.filter(path=obj).order_by('stop').iterator():
            dict = CustomerSerializer(c.customer).data
            ret.append(dict)
        return ret

    class Meta:
        model = Path
        fields = ['id', 'vehicle', 'vehicle_id', 'warehouse', 'warehouse_id', 'customers', 'leavetime', 'returntime']

class PlanSerializer(serializers.ModelSerializer):
    scenario = ScenarioSerializer(read_only=True)
    # scenario_id = serializers.PrimaryKeyRelatedField(source='scenario', write_only=True, queryset=Scenario.objects.all())
    paths = PathSerializer(many=True, read_only=True)
    # path_ids = serializers.PrimaryKeyRelatedField(source='paths', many=True, write_only=True, queryset=Path.objects.all())

    class Meta:
        model = Plan
        fields = ['id', 'tag', 'scenario', 'paths']
        # read_only_fields = fields

class Plan2Serializer(serializers.Serializer):
    id = serializers.IntegerField()
    tag = serializers.CharField(max_length=100)
    scenario = Scenario2Serializer(read_only=True)
    paths = serializers.SerializerMethodField()

    def get_paths(self, obj):
        ret=[]
        for path in Path.objects.filter(plan=obj).iterator():
            p_dict = PathSerializer(path).data
            ret.append(p_dict)
        return ret

class PlanShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'tag']
        # read_only_fields = fields

class DataLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataLog
        fields = ['id', 'action', 'time']

class DLSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataLog
        fields = ['id', 'user', 'session', 'action', 'time']

class VDSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleDemo
        fields = ['id', 'xmlstring', 'team', 'tag']

class OPDSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpsPlanDemo
        fields = ['id', 'xmlstring', 'team', 'tag']

class SDSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioDemo
        fields = ['id', 'xmlstring', 'team', 'tag']

class PDSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayDemo
        fields = ['id', 'xmlstring', 'team', 'tag']
