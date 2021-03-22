from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .serializers import SessionSerializer
from .models import Session, SessionTeam, Position, UserPosition, Group, UserChecklist, Market, Structure, Experiment, Organization, Study, Exercise, DigitalTwin
from django.db.models import Q, Subquery
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from repo.models import DesignTeam, Profile, Address, Warehouse, Vehicle, Scenario, Vehicle, Plan, CustomerScenario, Path, PathCustomer
from repo.models import DataLog
from repo.serializers import VehicleSerializer, Plan2Serializer, Scenario2Serializer
from chat.models import Channel
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from chat.messaging import new_precheck_message, new_postcheck_message
import csv
import json
from ai.agents.adaptive_team_ai_updated_planner import AdaptiveTeamAIUpdatedPlanner
from exper.serializers import DigitalTwinSerializer
from api.models import SessionTimer
from datetime import datetime, timezone
from ai.tasks import mediation_loop, human_mediation_loop
from design.utilities import cache_bust

# Create your views here.


class ActiveSessionList(generics.ListAPIView):
    """
    List all of the active sessions.
    """
    serializer_class = SessionSerializer

    def get_queryset(self):
        return Session.objects.filter(status__in=Session.ACTIVE_STATES)

class ActiveSession(generics.RetrieveAPIView):
    """
    Return the user's active session.
    """
    serializer_class = SessionSerializer

    def get_object(self):
        session_team = SessionTeam.objects.filter(Q(team=self.request.user.profile.team)&Q(session__status__in=Session.ACTIVE_STATES)).first()
        return session_team.session

class ExperimenterSessions(generics.ListAPIView):
    """
    Get sessions available to experimenter
    """
    serializer_class = SessionSerializer

    def get_queryset(self):
        print("get_queryset1")
        profile = Profile.objects.filter(user=self.request.user).first()
        print("get_queryset")
        if profile.organization:
            print("profile.organization")
            teams = DesignTeam.objects.filter(organization=profile.organization)
            session_teams = SessionTeam.objects.filter(team__in=teams)
            sessions = Session.objects.filter(id__in=session_teams).order_by('id')
            return sessions
        else:
            return Session.objects.all().order_by('id')

class DigitalTwinList(generics.ListCreateAPIView):
    """
    Show all digital twin object
    """
    parser_classes = [JSONParser]
    serializer_class = DigitalTwinSerializer
    def get_queryset(self):
        user = self.request.user
        organization = user.profile.organization.name
        organization_digital_twin = []
        all_digital_twins = DigitalTwin.objects.all()
        for digital_twin in all_digital_twins:
            print("restrict visibility to org", digital_twin.user_position.position.structure.organization)
            organization_digital_twin.append(digital_twin)
        return organization_digital_twin

class DigitalTwinDetail(APIView):
    """
    Show one digital twin object
    """

    serializer_class = DigitalTwinSerializer
    def get_object(self, ver):
        return DigitalTwin.objects.get(id=ver)

    def get(self, request, ver=-1):
        digital_twin = self.get_object(ver)
        serializer = DigitalTwinSerializer(digital_twin)
        return Response(serializer.data)

    def put(self, request, ver=-1):

        # grab the last version of the scenario
        digital_twin = self.get_object(ver)
        digital_twin.open_time_interval = request.data['open_time_interval']
        digital_twin.save_time_interval = request.data['save_time_interval']
        digital_twin.quality_bias = request.data['quality_bias']
        digital_twin.self_bias = request.data['self_bias']
        digital_twin.temperature = request.data['temperature']
        digital_twin.satisficing_factor = request.data['satisficing_factor']
        digital_twin.save()

        serializer = DigitalTwinSerializer(digital_twin)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    #def get(self, request, ver=-1):
    #    digital_twin = DigitalTwin.objects.filter(id=ver)
    #    serializer = DigitalTwinSerializer(digital_twin)
    #    return Response(serializer.data)

@api_view(['GET'])
def log_view(request, session_id):
    # Create the HttpResponse object with the appropriate CSV header.
    if request.user.is_authenticated:
        session = Session.objects.get(id=session_id)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="' + str(session_id)+'_SessionLog.csv"'

        writer = csv.writer(response)
        writer.writerow(['Time', 'User', 'Action', 'Type'])
        for log in DataLog.objects.filter(session=session).iterator():
            writer.writerow([log.time, log.user, log.action, log.type])

        return response
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

class VehicleList(generics.ListAPIView):
    """
    Get vehicles created in a session
    """
    serializer_class = VehicleSerializer

    def get_queryset(self):
        session_id = self.kwargs['session_id']
        return Vehicle.objects.filter(session=session_id)

class PlanList(generics.ListAPIView):
    """
    Get plans created in a session
    """
    serializer_class = Plan2Serializer

    def get_queryset(self):
        session_id = self.kwargs['session_id']
        return Plan.objects.filter(session=session_id)

class ScenarioList(generics.ListAPIView):
    """
    Get plans created in a session
    """
    serializer_class = Scenario2Serializer

    def get_queryset(self):
        session_id = self.kwargs['session_id']
        return Scenario.objects.filter(session=session_id)

@api_view(['PUT'])
def select_organization(request):
    if request.user.is_authenticated and request.user.profile.is_experimenter():
        orgId = request.data.get('orgId')
        if orgId:
            org = Organization.objects.filter(id=orgId).first()
            if org:
                studies = Study.objects.filter(organization=org)
                studies_dict = {}
                for study in studies:
                    studies_dict[study.name] = study.id
                return JsonResponse(json.dumps(studies_dict), safe=False)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
def select_study(request):
    if request.user.is_authenticated and request.user.profile.is_experimenter():
        studyId = request.data.get('studyId')
        if studyId:
            study = Study.objects.filter(id=studyId).first()
            if study:
                experiments = Experiment.objects.filter(study=study)
                experiments_dict = {}
                for experiment in experiments:
                    experiments_dict[experiment.name] = experiment.id
                return JsonResponse(json.dumps(experiments_dict), safe=False)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['PUT'])
def continue_to_experiment(request):
    if request.user.is_authenticated and request.user.profile.is_experimenter():
        # start a designer agent as a test
        orgId = request.data.get('orgId')
        studyId = request.data.get('studyId')
        expId = request.data.get('expId')
        if orgId and studyId and expId:
            org = Organization.objects.filter(id=orgId).first()
            study = Study.objects.filter(id=studyId).first()
            experiment = Experiment.objects.filter(id=expId).first()
            if org and study and experiment:
                request.user.profile.organization = org
                request.user.profile.study = study
                request.user.profile.experiment = experiment
                request.user.save()
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
def change_selection(request):
    if request.user.is_authenticated and request.user.profile.is_experimenter():
        # Don't null organization to prevent potential errors elsewhere
        request.user.profile.study = None
        request.user.profile.experiment = None
        request.user.save()
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
def session_status_play(request):
    if request.user.is_authenticated:
        if request.user.profile.is_experimenter():
            session = Session.objects.filter(id=request.data.get('id')).first()
            has_next = False
            next_session = Session.objects.filter(exercise=session.exercise).filter(index=session.index+1).first()
            if next_session:
                has_next = True
            if session:
                new_status = Session.STOPPED
                if session.status == Session.STOPPED:
                    #check if there are any active sessions for the same session team
                    session_teams = SessionTeam.objects.filter(session = session)
                    for session_team in session_teams:
                        team = session_team.team
                        if team:
                            team_sessions = SessionTeam.objects.filter(team = team)
                            for team_session in team_sessions:
                                team_session_session = team_session.session
                                if team_session_session and team_session_session.status in Session.ACTIVE_STATES:
                                    return Response(status=status.HTTP_409_CONFLICT)
                    new_status = Session.SETUP
                elif session.status == Session.SETUP:
                    new_status = Session.PRESESSION
                elif session.status == Session.PRESESSION:
                    new_status = Session.RUNNING
                    
                    # Update the session's RUNNING start timer
                    running_timer = SessionTimer.objects.filter(session=session).filter(timer_type=SessionTimer.RUNNING_START).first()
                    if running_timer:
                        running_timer.timestamp = datetime.now(timezone.utc)
                        running_timer.save()
                    else:
                        SessionTimer.objects.create(timer_type=SessionTimer.RUNNING_START, timestamp=datetime.now(timezone.utc), session=session)

                    if session.structure.name == "Process Manager":
                        print("Human Process Manager")
                        data = {}
                        data['session_id'] = session.id
                        human_mediation_loop.delay(data)
                        
                    elif session.structure.name == "Process Manager (AI)":
                        print("AI Process Manager")
                        data = {}
                        data['session_id'] = session.id
                        mediation_loop.delay(data)                  

                elif session.status == Session.RUNNING:
                    new_status = Session.POSTSESSION
                elif session.status == Session.POSTSESSION:
                    new_status = Session.ARCHIVED
                else:
                    new_status = Session.STOPPED
                session.status = new_status
                session.save()
                session_channel = Channel.objects.filter(name="Session").first()
                session_instance = str(session_channel.id) + "___" + str(session.id)

                async_to_sync(get_channel_layer().group_send)(
                    session_instance,
                    {
                        'type': 'system.command',
                        'message': "refresh",
                        'sender': "System",
                        'channel': session_instance
                    }
                )
                return JsonResponse({'new_status': new_status, 'has_next': has_next}, safe=False)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
def session_status_stop(request):
    if request.user.is_authenticated:
        if request.user.profile.is_experimenter():
            session = Session.objects.filter(id=request.data.get('id')).first()
            if session:
                session.status = request.data.get('newstatus')
                if session.status:
                    session.save()
                    session_channel = Channel.objects.filter(name="Session").first()
                    session_instance = str(session_channel.id) + "___" + str(session.id)
                    async_to_sync(get_channel_layer().group_send)(
                        session_instance,
                        {
                            'type': 'system.command',
                            'message': "refresh",
                            'sender': "System",
                            'channel': session_instance
                        }
                    )
                    return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
def session_status_archive(request):
    if request.user.is_authenticated:
        if request.user.profile.is_experimenter():
            session = Session.objects.filter(id=request.data.get('id')).first()
            if session:
                isTeam = True
                # TODO: Make individual/team a property of Structure
                if session.structure.name == "Extra":
                    isTeam = False
                next_session = Session.objects.filter(exercise=session.exercise).filter(index=session.index+1).first()
                if next_session:
                    same_market = True
                    if session.market != next_session.market:
                        same_market = False
                    group = Group.objects.filter(Q(name="All")&Q(structure=next_session.structure)).first()
                    vehicleMap = {}
                    if same_market:
                        #if these are copied over with different markets, the new session will see old market
                        for s in Scenario.objects.filter(session=session).iterator():
                            originalpk = s.pk
                            s.pk=None
                            s.session=next_session
                            if isTeam:
                                s.group=group
                            s.save()
                            for c in CustomerScenario.objects.filter(scenario=originalpk).iterator():
                                c.pk=None
                                c.scenario = s
                                c.save()
                    warehouse = Warehouse.objects.filter(session=next_session).first()
                    for v in Vehicle.objects.filter(session=session).iterator():
                        oldVehicleId = v.pk
                        v.pk=None
                        v.session=next_session
                        if isTeam:
                            v.group=group
                        v.save()
                        vehicleMap[oldVehicleId] = v
                    if same_market:
                        for p in Plan.objects.filter(session=session).iterator():
                            originalpk = p.pk
                            p.pk=None
                            p.session=next_session
                            if isTeam:
                                p.group=group
                            p.save()
                            for pth in Path.objects.filter(plan=originalpk).iterator():
                                originalpthpk = pth.pk
                                pth.pk=None
                                pth.session=next_session
                                pth.plan=p
                                pth.vehicle=vehicleMap[pth.vehicle.pk]
                                pth.warehouse = warehouse
                                pth.save()
                                for pc in PathCustomer.objects.filter(path=originalpthpk).iterator():
                                    pc.pk=None
                                    pc.path=pth
                                    pc.save()

                session.status = request.data.get('newstatus')
                if session.status:
                    session.save()

                    next_id = None
                    goto_next = request.data.get('goto_next')
                    if goto_next:
                        if next_session:
                            next_session.status=Session.PRESESSION
                            next_session.save()
                            next_id = next_session.id
                    session_channel = Channel.objects.filter(name="Session").first()
                    session_instance = str(session_channel.id) + "___" + str(session.id)
                    async_to_sync(get_channel_layer().group_send)(
                        session_instance,
                        {
                            'type': 'system.command',
                            'message': "refresh:exper", #exper means experimenter should refresh also
                            'sender': "System",
                            'channel': session_instance
                        }
                    )
                    if next_id and goto_next:
                        return JsonResponse({'next_id': next_id}, safe=False)
                    return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
def create_session_group(request):
    if request.user.is_authenticated and request.user.profile.is_experimenter():
        teamId = request.data.get('teamId')
        data = request.data.get('newSessionList')
        newSessionList  = json.loads(data)
        if len(newSessionList) < 1:
            return Response(status=status.HTTP_200_OK)

        experiment = request.user.profile.experiment
        newExercise = Exercise.objects.create(experiment=experiment)
        sessionIndex = 0

        team = DesignTeam.objects.filter(id=teamId).first()
        for item in newSessionList:
            sessionIndex = sessionIndex + 1
            sessionName = item['name']
            sessionUseAI = item['ai']
            sessionStructureId = item['structure']
            sessionStructure = Structure.objects.filter(id=sessionStructureId).first()
            sessionUseAIProcess = item['process']
            if sessionStructure.name != 'Process Manager':
                sessionUseAIProcess = False
            sessionMarketId = item['market']
            sessionMarket = Market.objects.filter(id=sessionMarketId).first()
            newSession = Session.objects.create(name=sessionName, experiment=experiment, exercise=newExercise, index=sessionIndex, prior_session=None, structure=sessionStructure, market=sessionMarket, use_ai=sessionUseAI, use_process_ai=sessionUseAIProcess, status=4)
            sessionTeam = SessionTeam.objects.create(team=team, session=newSession)
            structurePositions = list(Position.objects.filter(structure=sessionStructure).order_by('name'))

            profiles = Profile.objects.filter(team=team)
            teamUsers = list(User.objects.filter(id__in=Subquery(profiles.values('user'))).order_by('username'))
            numUsers = len(teamUsers)

            numPos = len(structurePositions)
            positer = numUsers
            if numPos < positer:
                positer = numPos
            for x in range(positer):
                UserPosition.objects.create(position=structurePositions[x], user=teamUsers[x], session=newSession)

            warehouseAddress = Address.objects.filter(region="warehouse").first()
            warehouseGroup = Group.objects.filter(name="All", structure=sessionStructure).first()
            Warehouse.objects.create(address=warehouseAddress, group=warehouseGroup, session=newSession)

            if sessionIndex == 1:
                baseConfig = "*aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3"
                Vehicle.objects.create(tag="base", config=baseConfig, result="Success", range=10.0, velocity=20.0, cost=3470.20043945312, payload=5, group=warehouseGroup, session=newSession)
                print("session vehicle add")

        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
def change_user_password(request):
    newpassword = request.data.get('newpassword')
    newpassword_id = request.data.get('newpassword_id')
    if request.user.is_authenticated and newpassword:
        if request.user.profile.is_experimenter():
            user_profile = Profile.objects.filter(user__id=newpassword_id).first()
            up_user = user_profile.user
            if user_profile.is_player():
                up_user.set_password(newpassword)
                up_user.save()
                user_profile.temp_code = newpassword
                user_profile.save()
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
def change_org_password(request):
    newpassword = request.data.get('newpassword')
    if request.user.is_authenticated and newpassword:
        if request.user.profile.is_experimenter():
            profile = request.user.profile
            organization = profile.organization
            if organization:
                org_teams = DesignTeam.objects.filter(organization=profile.organization)
                for team in org_teams:
                    user_profiles = Profile.objects.filter(team=team)
                    for user_profile in user_profiles:
                        # Don't reset Experimentor passwords
                        # The shouldn't be part of a team, but may be since database
                        # doesn't enforce that they aren't
                        up_user = user_profile.user
                        if user_profile.is_player():
                            up_user.set_password(newpassword)
                            up_user.save()
                            user_profile.temp_code = newpassword
                            user_profile.save()
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
def pre_check(request):
    is_checked = request.data.get('is_checked')
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            current_checklist = UserChecklist.objects.filter(user=request.user).filter(session=st.session).first()
            if not current_checklist:
                current_checklist = UserChecklist.objects.create(user=request.user, session=st.session)
            if is_checked and is_checked == "true":
                current_checklist.precheck = True
                current_checklist.save()
            else :
                current_checklist.precheck = False
                current_checklist.save()
            new_precheck_message(request.user, st.session, current_checklist.precheck)
    return Response(status=status.HTTP_200_OK)


@api_view(['PUT'])
def post_check(request):
    is_checked = request.data.get('is_checked')
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            current_checklist = UserChecklist.objects.filter(user=request.user).filter(session=st.session).first()
            if not current_checklist:
                current_checklist = UserChecklist.objects.create(user=request.user, session=st.session)
            if is_checked and is_checked == "true":
                current_checklist.postcheck = True
                current_checklist.save()
            else :
                current_checklist.postcheck = False
                current_checklist.save()
            new_postcheck_message(request.user, st.session, current_checklist.postcheck)
    return Response(status=status.HTTP_200_OK)

@api_view(['PUT'])
def create_structure(request):
    channel_data = request.data.get('channelData')
    print(str(channel_data))
    return Response(status=status.HTTP_200_OK)

@api_view(['PUT'])
def start_digital_twin(request):
    if request.user.is_authenticated:
        if request.user.profile.is_experimenter():
            session = Session.objects.filter(id=request.data.get('id')).first()
            # archive it
#            session.status = 5
#            session.save()
            digital_twin_setups = get_digital_twin_for_session(int(request.data.get('id')))
            t = AdaptiveTeamAIUpdatedPlanner(session, digital_twin_setups)
            return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def digital_twin(request, session_id):
    if request.user.is_authenticated and request.user.profile.is_experimenter():
        session = Session.objects.filter(id=session_id).first()
        digital_twin_setups = get_digital_twin_for_session(session_id)
        context = {
            'session': session,
            'session_id' : session_id,
            'digital_twin_setups' : digital_twin_setups
        }
        context['BUST'] = cache_bust()
        response = HttpResponse(render(request, "digitaltwinedit.html", context))
    else:
        response = HttpResponse(render(request, "digitaltwinedit.html", context))
    return response

def get_digital_twin_for_session(session_id):

    session_user_positions = []
    user_positions = UserPosition.objects.all()     # for some reason , filter does not work, fix this
    for user in user_positions:
        if user.session.id == session_id:
            session_user_positions.append(user)

    digital_twin_setups = []
    # query or create digital twin objects
    for user in session_user_positions:
        digital_twin_setup = DigitalTwin.objects.filter(user_position=user)
        if len(digital_twin_setup) == 0:
            new_setup = DigitalTwin.objects.create(user_position=user)
            new_setup.save()
            digital_twin_setups.append(new_setup)
        else:
            digital_twin_setups.append(digital_twin_setup[0])

    return digital_twin_setups
