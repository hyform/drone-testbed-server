from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .serializers import ChannelPositionSerializer, ChannelSerializer
from .models import ChannelPosition, Channel
from repo.models import Profile
from rest_framework import generics
from exper.models import UserPosition, SessionTeam, Session, UserChecklist


# Create your views here.

@login_required
def index(request):
    context = {}
    experimenter = False
    if request.user.is_authenticated:        
        expcheck = Profile.objects.filter(user=request.user, is_exper=True)
        if expcheck:
            experimenter = True            
        else:
            st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
            if st:
                up = UserPosition.objects.filter(Q(user=request.user) & Q(session=st.session)).first()
                if up:
                    position = up.position
                    if position:
                        context['position_name'] = position.name
    context['experimenter'] = experimenter                    
    return render(request, 'chat/index.html', context)

class ChannelList2(generics.ListAPIView):
    """
    List all the channels for the given user.
    """
    serializer_class = ChannelPositionSerializer

    def get_queryset(self):
        user = self.request.user
        ups = UserPosition.objects.filter(user=self.request.user)
        session = SessionTeam.objects.filter(Q(session__status=1)&Q(team=user.profile.team)).first()
        up = UserPosition.objects.filter(Q(user=self.request.user) & Q(session=session.session)).first()
        return ChannelPosition.objects.filter(position=up.position)

class ChannelList(generics.ListAPIView):
    """
    List all the channels for the given user.
    """
    serializer_class = ChannelSerializer

    def get_queryset(self):
        user = self.request.user
        channel_list = Channel.objects.none()

        ups = UserPosition.objects.filter(user=self.request.user)
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=user.profile.team)).first()
        if st:
            help_channel = Channel.objects.filter(name="Help")
            if st.session.status == Session.RUNNING:
                up = UserPosition.objects.filter(Q(user=self.request.user) & Q(session=st.session)).first()
                channel_positions = ChannelPosition.objects.filter(position=up.position)
                user_channels = Channel.objects.filter(id__in=channel_positions.values('channel'))
                channel_list = user_channels | help_channel
            elif st.session.status == Session.SETUP:
                setup_channel = Channel.objects.filter(name="Setup")
                channel_list = setup_channel
            else:
                channel_list = help_channel
        channel_list = Channel.objects.none()
        return channel_list


class ChannelExperList(generics.ListAPIView):
    """
    List all of the help channels for the experimenter.
    """

    serializer_class = ChannelSerializer

    def get_queryset(self):
        team_id = self.kwargs['team_id']
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team__id=team_id)).first()
        user = self.request.user
        # channel_list = Channel.objects.filter(name="Help")
        channel_list = Channel.objects.none()
        return channel_list
