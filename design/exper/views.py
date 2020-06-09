from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .serializers import SessionSerializer
from .models import Session, SessionTeam, Position, UserPosition, Group, UserChecklist, Market, Structure, Experiment
from django.db.models import Q, Subquery
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from repo.models import DesignTeam, Profile, Address, Warehouse, Vehicle, Scenario, Vehicle, Plan, CustomerScenario, Path, PathCustomer
from repo.models import DataLog
from repo.serializers import VehicleSerializer, Plan2Serializer, Scenario2Serializer
from chat.models import Channel
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from chat.messaging import new_precheck_message, new_postcheck_message
import csv

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
def session_status_play(request):
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user = request.user).first()
        if profile and profile.is_exper:
            session = Session.objects.filter(id=request.data.get('id')).first()
            has_next = False
            next_session = Session.objects.filter(prior_session=session).first()
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
        profile = Profile.objects.filter(user = request.user).first()
        if profile and profile.is_exper:
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
        profile = Profile.objects.filter(user = request.user).first()
        if profile and profile.is_exper:
            session = Session.objects.filter(id=request.data.get('id')).first()
            if session:
                isTeam = True
                # TODO: Make individual/team a property of Structure
                if session.structure.name == "Extra":
                    isTeam = False
                next_session = Session.objects.filter(prior_session=session).first()
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
    if request.user.is_authenticated:
        teamId = request.data.get('teamId')
        session1Name = request.data.get('session1Name')
        session1AI =request.data.get('session1AI')
        session1StructureId = request.data.get('session1StructureId')
        session1MarketId = request.data.get('session1MarketId')
        create2nd = request.data.get('create2nd')
        session2Name = request.data.get('session2Name')
        session2AI =request.data.get('session2AI')
        session2StructureId = request.data.get('session2StructureId')
        session2MarketId = request.data.get('session2MarketId')

        team = DesignTeam.objects.filter(id=teamId).first()

        experiment = Experiment.objects.filter(user=request.user).first()
        if not experiment:
            experiment = Experiment.objects.all().first()

        session1UseAI = True
        if session1AI == "false":
            session1UseAI = False
        session1Structure = Structure.objects.filter(id=session1StructureId).first()
        session1Market = Market.objects.filter(id=session1MarketId).first()
        newSession1 = Session.objects.create(name=session1Name, experiment=experiment, prior_session=None, structure=session1Structure, market=session1Market, use_ai=session1UseAI, status=4)
        sessionTeam1 = SessionTeam.objects.create(team=team, session=newSession1)
        strusture1Positions = list(Position.objects.filter(structure=session1Structure).order_by('name'))

        profiles = Profile.objects.filter(team=team)
        teamUsers = list(User.objects.filter(id__in=Subquery(profiles.values('user'))).order_by('username'))
        numUsers = len(teamUsers)

        numPos1 = len(strusture1Positions)
        pos1iter = numUsers
        if numPos1 < pos1iter:
            pos1iter = numPos1
        for x in range(pos1iter):
            UserPosition.objects.create(position=strusture1Positions[x], user=teamUsers[x], session=newSession1)

        warehouseAddress = Address.objects.filter(region="warehouse").first()
        warehouse1Group = Group.objects.filter(name="All", structure=session1Structure).first()
        Warehouse.objects.create(address=warehouseAddress, group=warehouse1Group, session=newSession1)

        baseConfig = "*aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3"
        Vehicle.objects.create(tag="base", config=baseConfig, result="Success", range=10.6703462600708, velocity=8.86079978942871, cost=3470.20043945312, payload=5, group=warehouse1Group, session=newSession1)

        if create2nd == "true":
            session2UseAI = True
            if session2AI == "false":
                session2UseAI = False
            session2Structure = Structure.objects.filter(id=session2StructureId).first()
            session2Market = Market.objects.filter(id=session2MarketId).first()
            newSession2 = Session.objects.create(name=session2Name, experiment=experiment, prior_session=newSession1, structure=session2Structure, market=session2Market, use_ai=session2UseAI, status=4)
            sessionTeam2 = SessionTeam.objects.create(team=team, session=newSession2)
            strusture2Positions = list(Position.objects.filter(structure=session2Structure).order_by('name'))

            numPos2 = len(strusture2Positions)
            pos2iter = numUsers
            if numPos2 < pos2iter:
                pos2iter = numPos2
            for y in range(pos2iter):
                UserPosition.objects.create(position=strusture2Positions[y], user=teamUsers[y], session=newSession2)

            warehouse2Group = Group.objects.filter(name="All", structure=session2Structure).first()
            Warehouse.objects.create(address=warehouseAddress, group=warehouse2Group, session=newSession2)

            #Session 2 should get seed data loaded from Session 1
            #Vehicle.objects.create(tag="base", config=baseConfig, group=warehouse2Group, session=newSession2)

        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['PUT'])
def change_user_password(request):
    newpassword = request.data.get('newpassword')
    newpassword_id = request.data.get('newpassword_id')
    if request.user.is_authenticated and newpassword:
        profile = Profile.objects.filter(user = request.user).first()
        if profile and profile.is_exper:
            user_profile = Profile.objects.filter(user__id=newpassword_id).first()
            up_user = user_profile.user
            if not user_profile.is_exper and up_user and not up_user.is_superuser:
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
        profile = Profile.objects.filter(user = request.user).first()
        if profile and profile.is_exper:
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
                        if not user_profile.is_exper and up_user and not up_user.is_superuser:
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
