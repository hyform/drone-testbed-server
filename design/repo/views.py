from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status, mixins, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ValidationError
from django.views import generic
from repo.models import DesignTeam, Vehicle, Address, Customer, CustomerScenario, Warehouse, Scenario, Waypoint, Path, Plan, DataLog
from repo.models import VehicleDemo, ScenarioDemo, OpsPlanDemo, PlayDemo, PathCustomer
from repo.serializers import UserSerializer, TeamSerializer, VehicleSerializer, AddressSerializer, CustomerSerializer, WarehouseSerializer
from repo.serializers import ScenarioSerializer, WaypointSerializer, PathSerializer, PlanSerializer, DataLogSerializer
from repo.serializers import DLSerializer, VDSerializer, SDSerializer, OPDSerializer, PDSerializer, Plan2Serializer, PlanShortSerializer
from django.http import Http404
from exper.models import UserPosition, SessionTeam, GroupPosition, Session
from django.db.models import Q
from chat.messaging import new_vehicle_message, new_plan_message, new_scenario_message
import time

class VehicleList(generics.ListCreateAPIView):
    """
    List all vehicle entries, or create a new vehicle entry.
    """
    # queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    def get_queryset(self):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        if st:
            up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
            groups = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure)).values('group')
            qs = Vehicle.objects.filter(group__in=groups, session=st.session)
        else:
            qs = Vehicle.objects.none()
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        if st:
            up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
            gp = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure)&Q(primary=True)).first()
            # self.request.data['group']=gp.group.id
            # self.request.data['session']=st.session.id
            # serializer.save(data=self.request.data)
            serializer.save(group=gp.group, session=st.session)
            tag = None
            data = self.request.data
            if 'tag' in data:
                tag = data['tag']
            new_vehicle_message(gp.group, st.session, tag)
        else:
            raise ValidationError('You are not in an active session')


class VehicleDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a vehicle entry.
    """
    # queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    def get_queryset(self):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
        groups = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure)).values('group')
        return Vehicle.objects.filter(group__in=groups, session=st.session)


class ScenarioDetail(APIView):
    """
    Retreive or Create a scenario entry.
    """
    parser_classes = [JSONParser]

    def get_object(self, request, ver):
        # the default version of -1 means return the last version
        # if not scenario exists for this session/group combo - create a new one
        user = request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        if st==None:
            return None
        up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
        groups = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure))
        scenarios = Scenario.objects.filter(Q(group__in=groups.values('group'))&Q(session=st.session))
        if scenarios.exists():
            # there is at least one scenario already
            if ver==-1:
                # the default is to return the last one
                return scenarios.order_by('version').last()
            else:
                return scenarios.get(version=ver)
        else:
            # this will make a new scenario
            warehouse = Warehouse.objects.filter(Q(group__in=groups.values('group'))&Q(session=st.session)).first()
            group = groups.filter(primary=True).first()
            scenario = Scenario.objects.create(tag='Initial Scenario', warehouse=warehouse, group=group.group, session = st.session)
            # also need to select all of the customer's in this market
            market = st.session.market
            customers = Customer.objects.filter(market=market)
            for customer in customers:
                # this may be a little slow - keep an eye on it
                # may want to create a lsit of objects and then use bulk_create
                CustomerScenario.objects.create(customer=customer, scenario=scenario, selected=True)
            return scenario


    def get(self, request, ver=-1):
        scenario = self.get_object(request, ver)
        serializer = ScenarioSerializer(scenario)
        return Response(serializer.data)


    def put(self, request, ver=-1):
        # grab the last version of the scenario
        scenario = self.get_object(request, ver)
        # get all of the customers
        customers = Customer.objects.filter(market=scenario.session.market)
        # increment version number
        tag = request.data.get('tag', scenario.tag)
        scenario = Scenario.objects.create(tag=tag, warehouse=scenario.warehouse, group=scenario.group, session=scenario.session, version=scenario.version+1)
        clist = request.data.get('customers', [])
        for customer in customers:
            if customer.id in clist:
                CustomerScenario.objects.create(customer=customer, scenario=scenario, selected=True)
            else:
                CustomerScenario.objects.create(customer=customer, scenario=scenario, selected=False)
        new_scenario_message(scenario.group, scenario.session)
        return Response(status=status.HTTP_201_CREATED)


class PlanList(generics.ListCreateAPIView):
    """
    List all plan entries or create a new plan entry
    """
    # queryset = Plan.objects.all()
    def get_queryset(self):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        # may want to add a test to make sure the user is in an active session before continuing
        up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
        groups = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure)).values('group')
        start_time = time.time()
        plans = Plan.objects.filter(Q(group__in=groups)&Q(session=st.session))
        print("time to get plans - %s secs" % (time.time() - start_time))
        return plans
        # return Plan.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        # may want to add a test to make sure the user is in an active session before continuing
        up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
        gp = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure)&Q(primary=True)).first()
        # first step is to create a plan object
        data = self.request.data
        scenario = Scenario.objects.get(id=data.get('scenario'))
        plan = Plan.objects.create(tag=data.get('tag'), scenario=scenario, group=gp.group, session=st.session)
        # next is to create the path objects
        paths = data.get('paths')
        for p in paths:
            vehicle = Vehicle.objects.get(id=p.get('vehicle'))
            warehouse = Warehouse.objects.get(id=p.get('warehouse'))
            path = Path.objects.create(plan=plan, vehicle=vehicle, warehouse=warehouse, leavetime=p.get('leavetime',0.0),
                returntime=p.get('returntime',0.0))
            # next we need to define the customers in the path
            customers = p.get('customers')
            stop=1
            for c in customers:
                customer = Customer.objects.get(id=c)
                PathCustomer.objects.create(path=path, customer=customer, stop=stop)
                stop=stop+1
        new_plan_message(gp.group, st.session, plan.tag)
        # return Response(status=status.HTTP_201_CREATED)

    serializer_class = PlanSerializer

class Plan2List(generics.ListAPIView):
    """
    List all plan entries or create a new plan entry
    """
    # queryset = Plan.objects.all()
    def get_queryset(self):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        # may want to add a test to make sure the user is in an active session before continuing
        up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
        groups = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure)).values('group')
        start_time = time.time()
        plans = Plan.objects.filter(Q(group__in=groups)&Q(session=st.session))
        print("time to get plans - %s secs" % (time.time() - start_time))
        return plans
        # return Plan.objects.all()

    serializer_class = Plan2Serializer
class PlanShortList(generics.ListAPIView):
    """
    List all plan entries for the session - short version
    """
    def get_queryset(self):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        # may want to add a test to make sure the user is in an active session before continuing
        up = UserPosition.objects.filter(Q(user=user)&Q(session=st.session)).first()
        groups = GroupPosition.objects.filter(Q(position=up.position)&Q(position__structure=st.session.structure)).values('group')
        start_time = time.time()
        plans = Plan.objects.filter(Q(group__in=groups)&Q(session=st.session)).order_by('id')
        print("time to get plans - %s secs" % (time.time() - start_time))
        return plans

    serializer_class = PlanShortSerializer

class PlanDetail(generics.RetrieveAPIView):
    """
    Retrieve a plan entry.
    """

    queryset = Plan.objects.all()
    serializer_class = PlanSerializer


class DataLogList(generics.CreateAPIView):
    """
    Create a new DataLog Entry
    """
    # queryset = DataLog.objects.all()
    serializer_class = DataLogSerializer

    def perform_create(self, serializer):
        user = self.request.user
        st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        if st:
            serializer.save(user=user, session=st.session, type='client')
        else:
            raise ValidationError('You are not in an active session')


class DataLogDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retreive, Update, Delete a DataLog Entry
    """
    queryset = DataLog.objects.all()
    serializer_class = DataLogSerializer

class DataLogListView(generic.ListView):

    def get_queryset(self):
        # if self.request.user.profile.is_exper is True:
        #    team = self.request.get('team','')
        # else:
        #    team = self.request.user.username.split('_')[0]
        # return DataLog.objects.filter(team=team).order_by('time')
        user = self.request.user
        session = Session.objects.get(id=self.kwargs['session_id'])
        # st = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        if session:
            log = DataLog.objects.filter(session=session).order_by('-time')
        else:
            log = None
        return log

    def get_context_data(self, **kwargs):
        context = super(DataLogListView, self).get_context_data(**kwargs)
        session = Session.objects.get(id=self.kwargs['session_id'])
        if session:
            context['session_name'] = session.name
        else:
            context['session_name'] = "Unknown"
        return context


    template_name = 'repo/datalog_list.html'




class DLAdminView(generics.ListAPIView):
    queryset = DataLog.objects.all()
    serializer_class = DataLogSerializer
    permission_classes = [IsAdminUser]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'repo/datalog_admin.html'


class VDList(generics.ListCreateAPIView):
    """
    List all target entries or create a new target entry
    """
    queryset = VehicleDemo.objects.all()
    serializer_class = VDSerializer

class VDDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retreive, Update, Delete a target entry.
    """
    queryset = VehicleDemo.objects.all()
    serializer_class = VDSerializer

class SDList(generics.ListCreateAPIView):
    """
    List all target entries or create a new target entry
    """
    queryset = ScenarioDemo.objects.all()
    serializer_class = SDSerializer

class SDDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retreive, Update, Delete a target entry.
    """
    queryset = ScenarioDemo.objects.all()
    serializer_class = SDSerializer

class OPDList(generics.ListCreateAPIView):
    """
    List all target entries or create a new target entry
    """
    queryset = OpsPlanDemo.objects.all()
    serializer_class = OPDSerializer

class OPDDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retreive, Update, Delete a target entry.
    """
    queryset = OpsPlanDemo.objects.all()
    serializer_class = OPDSerializer

class PDList(generics.ListCreateAPIView):
    """
    List all target entries or create a new target entry
    """
    queryset = PlayDemo.objects.all()
    serializer_class = PDSerializer

class PDDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retreive, Update, Delete a target entry.
    """
    queryset = PlayDemo.objects.all()
    serializer_class = PDSerializer
