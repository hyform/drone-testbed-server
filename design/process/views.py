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
from .messaging import send_intervention
from api.models import SessionTimer
from datetime import datetime

@api_view(['PUT'])
def intervention(request):
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            position = UserPosition.objects.filter(Q(session=st.session)&Q(user=request.user)).first().position
            if position and position.role.name == "Process":
                intervention = request.data.get('intervention')
                send_intervention(intervention, st.session.id)
                return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def elapsed_time(request):
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            position = UserPosition.objects.filter(Q(session=st.session)&Q(user=request.user)).first().position
            if position and position.role.name == "Process":
                '''
                running_timer = SessionTimer.objects.filter(session=st.session).filter(timer_type=SessionTimer.RUNNING_START).first()
                if running_timer:
                    current_time = datetime.now()
                    time_difference = current_time - running_timer.timestamp
                    elapsed_seconds = time_difference.total_seconds()
                else:
                    print("no running timer found")
                    elapsed_seconds = 0 
                '''
                elapsed_seconds = 0                  
                results = {}
                results["elapsed_seconds"] = elapsed_seconds
                return JsonResponse(results)
    return Response(status=status.HTTP_401_UNAUTHORIZED)