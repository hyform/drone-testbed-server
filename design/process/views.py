from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Subquery
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from exper.models import UserPosition, SessionTeam, Session
from chat.models import Channel
from .messaging import send_intervention
from api.models import SessionTimer
from repo.models import DesignTeam
from datetime import datetime, timezone

# Send an intervention
@api_view(['PUT'])
def intervention(request):
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            position = UserPosition.objects.filter(Q(session=st.session)&Q(user=request.user)).first().position
            if position and position.role.name == "Process":
                intervention = request.data.get('intervention')
                send_intervention(request.user, intervention, st.session.id)
                return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

# Get time after session entered Running status
@api_view(['POST'])
def elapsed_time(request):
    if request.user.is_authenticated:
        st = None
        data = request.data
        team_id = data.get('team')
        if team_id:
            st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team__id=team_id)).first()
        else:
            st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            running_timer = SessionTimer.objects.filter(session=st.session).filter(timer_type=SessionTimer.RUNNING_START).first()
            elapsed_seconds = -1
            if running_timer and st.session.status == Session.RUNNING:
                current_time = datetime.now(timezone.utc)
                running_timestamp = running_timer.timestamp
                if running_timestamp:
                    time_difference = current_time - running_timestamp
                    elapsed_seconds = round(time_difference.total_seconds())
            results = {}
            results['elapsed_seconds'] = elapsed_seconds
            return JsonResponse(json.dumps(results), safe=False)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

# Method to allow a Process Manager to exit the Running status of a session
# Automating this for now, but keep around since it might be useful for something
'''
@api_view(['PUT'])
def session_status_postsession(request):
    if request.user.is_authenticated:        
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            if st.session.status == Session.RUNNING:
                st.session.status = Session.POSTSESSION
                st.session.save()
                session_channel = Channel.objects.filter(name="Session").first()
                session_instance = str(session_channel.id) + "___" + str(st.session.id)

                async_to_sync(get_channel_layer().group_send)(
                    session_instance,
                    {
                        'type': 'system.command',
                        'message': "refresh",
                        'sender': "System",
                        'channel': session_instance
                    }
                )

                exercise = st.session.exercise
                if exercise:
                    experiment = exercise.experiment
                    if experiment:
                        study = experiment.study
                        if study:
                            organization = study.organization
                            if organization:
                                help_channel = Channel.objects.filter(name="Help").first()
                                channel_instance = str(help_channel.id) + "_organization_" + str(organization.id)
                                async_to_sync(get_channel_layer().group_send)(
                                    channel_instance,
                                    {
                                        'type': 'system.command',
                                        'message': "experimenter-reload",
                                        'sender': "System",
                                        'channel': channel_instance
                                    }
                                )
                return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_401_UNAUTHORIZED)
'''