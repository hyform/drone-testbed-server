from django.http import HttpResponse, Http404
from django.template import loader
from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Subquery
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from operator import attrgetter
from exper.models import Role, UserPosition, Structure
from exper.models import Session, SessionTeam, Market
from repo.models import Profile, DesignTeam
import collections

def ateams_homepage(request):
    context = {}
    response = None
    experimenter = False
    if request.user.is_authenticated:
        expcheck = Profile.objects.filter(user=request.user, is_exper=True)
        if expcheck:
            experimenter = True
        context['experimenter'] = experimenter
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            if st.session.status == Session.SETUP:
                context['redir'] = "/setup/"
            elif st.session.status == Session.PRESESSION:
                context['redir'] = "/presession/"
            elif st.session.status == Session.RUNNING:
                position = UserPosition.objects.filter(Q(session=st.session)&Q(user=request.user)).first().position
                if position:
                    if position.role.name == "Business":
                        context['redir'] = "/business/"
                    elif position.role.name == "OpsPlanner":
                        context['redir'] = "/ops/"
                    elif position.role.name == "Designer":
                        context['redir'] = "/design/"
            elif st.session.status == Session.POSTSESSION:
                context['redir'] = "/postsession/"
            response = HttpResponse(render(request, "home.html", context))
        else:
            if not experimenter:
                logout(request)
            response = HttpResponse(render(request, "home.html", context))
    else:
        response = HttpResponse(render(request, "home.html"))
    return response

@login_required
def ateams_experiment(request):
    profile = Profile.objects.filter(user=request.user).first()
    org_teams = None
    exp_sessions = None
    session_teams = None
    markets = None
    structures = None
    st_dict = {}
    session_next = {}
    all_users = dict()
    if profile.organization:
        org_teams = DesignTeam.objects.filter(organization=profile.organization)
        for org_team in org_teams:
            user_profiles = Profile.objects.filter(team=org_team)
            for user_profile in user_profiles:
                up_user = user_profile.user
                user_string = up_user.username + " : " + org_team.name
                all_users[user_string] = up_user.id
        org_teams_ids = org_teams.values('id')
        session_teams = SessionTeam.objects.filter(team_id__in=org_teams_ids)
        for st in session_teams:
            st_dict[st.session_id] = DesignTeam.objects.filter(id=st.team_id).first()
        exp_sessions = Session.objects.filter(id__in=session_teams.values('session_id')).order_by('id')
        for session in exp_sessions:
            # This assumes the prior session is in the organization
            # If it ever isn't, this code needs to be updated to check that
            if session.prior_session:
                session_next[session.prior_session] = session
        markets = Market.objects.all()
        structures = Structure.objects.all()

        sorted_all_users = collections.OrderedDict()
        for key, value in sorted(all_users.items()):
            sorted_all_users[key] = value

    context = {
        'org_teams': org_teams,
        'exp_sessions': exp_sessions,
        'session_teams': session_teams,
        'st_dict': st_dict,
        'session_next': session_next,
        'markets': markets,
        'structures': structures,
        'all_users': sorted_all_users,
    }
    response = HttpResponse(render(request, "experiment.html", context))
    if request.user.is_authenticated:
        response.set_cookie('username', request.user.username)
    return response

@login_required
def ateams_experiment_chat(request):
    template_sessions = None
    template_sessions = Session.objects.filter(status=Session.TEMPLATE)

    profile = Profile.objects.filter(user=request.user).first()
    org_teams = None
    exp_sessions = None
    session_teams = None
    st_dict = {}
    if profile.organization:
        org_teams = DesignTeam.objects.filter(organization=profile.organization)
        org_teams_ids = org_teams.values('id')
        session_teams = SessionTeam.objects.filter(team_id__in=org_teams_ids)
        # exp_sessions = Session.objects.filter(id__in=session_teams.values('session_id')).order_by('id')
        exp_sessions = Session.objects.filter(Q(id__in=session_teams.values('session_id'))&Q(status__in=Session.ACTIVE_STATES)).order_by('id')
        for st in session_teams:
            st_dict[st.session_id] = DesignTeam.objects.filter(id=st.team_id).first()

    context = {
        'template_sessions': template_sessions,
        'org_teams': org_teams,
        'exp_sessions': exp_sessions,
        'session_teams': session_teams,
        'st_dict': st_dict,
    }
    response = HttpResponse(render(request, "experimentchat.html", context))
    if request.user.is_authenticated:
        response.set_cookie('username', request.user.username)
    return response

@login_required
def ateams_temp_user_info(request):
    context = {}
    user_info = {}
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user = request.user).first()
        if profile and profile.is_exper:
            organization = profile.organization
            if organization:
                org_teams = DesignTeam.objects.filter(organization=profile.organization)
                for team in org_teams:
                    user_profiles = Profile.objects.filter(team=team)
                    for user_profile in user_profiles:
                        up_user = user_profile.user
                        if not user_profile.is_exper and up_user and not up_user.is_superuser:
                            user_info[up_user.username] = user_profile.temp_code
                sorted_user_info = collections.OrderedDict()
                for key, value in sorted(user_info.items()):
                    sorted_user_info[key] = value
                context["user_info"] = sorted_user_info
                return HttpResponse(render(request, "tempuserinfo.html", context))
    return HttpResponse(render(request, "home.html"))

@login_required
def ateams_setup(request):
    context = {}
    response = None
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            if st.session.status == Session.SETUP:
                is_team = True
                if st.session.structure.name == "Extra":
                    is_team = False
                context['is_team'] = is_team
                response = HttpResponse(render(request, "setup.html", context))
                response.set_cookie('use_ai', st.session.use_ai)
                response.set_cookie('username', request.user.username)
            else:
                if st.session.status == Session.PRESESSION:
                    context['redir'] = "/presession/"
                elif st.session.status == Session.RUNNING:
                    position = UserPosition.objects.filter(Q(session=st.session)&Q(user=request.user)).first().position
                    if position:
                        if position.role.name == "Business":
                            context['redir'] = "/business/"
                        elif position.role.name == "OpsPlanner":
                            context['redir'] = "/ops/"
                        elif position.role.name == "Designer":
                            context['redir'] = "/design/"
                elif st.session.status == Session.POSTSESSION:
                    context['redir'] = "/postsession/"
                response = HttpResponse(render(request, "setup.html", context))
        else:
            context['redir'] = "/"
            #logout(request)
            response = HttpResponse(render(request, "setup.html", context))
    else:
        response = HttpResponse(render(request, "home.html"))
    return response

@login_required
def ateams_presession(request):
    context = {}
    response = None
    role = None
    st = None
    pos = 0
    team_type = 0
    context['last'] = True
    context['first'] = True
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            context['session'] = st.session.structure.name
            if st.session.status == Session.PRESESSION:
                is_team = True
                if st.session.structure.name == "Extra":
                    is_team = False
                context['is_team'] = is_team
                next_sessions = Session.objects.filter(session__prior_session=st.session)
                if next_sessions:
                    context['last'] = False
                else:
                    context['first'] = False
                context['session_ai'] = st.session.use_ai
                up = UserPosition.objects.filter(Q(user=request.user)&Q(session=st.session)).first()
                pos_name = up.position.name
                context['pos_name'] = pos_name
                if "Design Manager" in pos_name:
                    pos = 1
                elif "Design Specialist" in pos_name:
                    pos = 2
                elif "Operations Manager" in pos_name:
                    pos = 3
                elif "Operations Specialist" in pos_name:
                    pos = 4
                elif "Business" in pos_name:
                    pos = 5

                role = up.position.role

                context['role'] = role
                context['position'] = pos

                response = HttpResponse(render(request, "presession.html", context))
                response.set_cookie('use_ai', st.session.use_ai)
                response.set_cookie('username', request.user.username)
            else:
                if st.session.status == Session.SETUP:
                    context['redir'] = "/setup/"
                elif st.session.status == Session.RUNNING:
                    position = UserPosition.objects.filter(Q(session=st.session)&Q(user=request.user)).first().position
                    if position:
                        if position.role.name == "Business":
                            context['redir'] = "/business/"
                        elif position.role.name == "OpsPlanner":
                            context['redir'] = "/ops/"
                        elif position.role.name == "Designer":
                            context['redir'] = "/design/"
                elif st.session.status == Session.POSTSESSION:
                    context['redir'] = "/postsession/"
                response = HttpResponse(render(request, "presession.html", context))
        else:
            context['redir'] = "/"
            #logout(request)
            response = HttpResponse(render(request, "presession.html", context))
    else:
        response = HttpResponse(render(request, "home.html"))
    return response

@login_required
def ateams_design(request):
    context = {}
    response = None
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            if st.session.status == Session.RUNNING:
                response = HttpResponse(render(request, "design.html"))
                response.set_cookie('use_ai', st.session.use_ai)
                response.set_cookie('username', request.user.username)
            else:
                if st.session.status == Session.SETUP:
                    context['redir'] = "/setup/"
                elif st.session.status == Session.PRESESSION:
                    context['redir'] = "/presession/"
                elif st.session.status == Session.POSTSESSION:
                    context['redir'] = "/postsession/"
                response = HttpResponse(render(request, "design.html", context))
        else:
            context['redir'] = "/"
            #logout(request)
            response = HttpResponse(render(request, "design.html", context))
    else:
        response = HttpResponse(render(request, "home.html"))
    return response

@login_required
def ateams_ops(request):
    context = {}
    response = None
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            if st.session.status == Session.RUNNING:
                response = HttpResponse(render(request, "ops.html"))
                response.set_cookie('use_ai', st.session.use_ai)
                response.set_cookie('username', request.user.username)
            else:
                if st.session.status == Session.SETUP:
                    context['redir'] = "/setup/"
                elif st.session.status == Session.PRESESSION:
                    context['redir'] = "/presession/"
                elif st.session.status == Session.POSTSESSION:
                    context['redir'] = "/postsession/"
                response = HttpResponse(render(request, "ops.html", context))
        else:
            context['redir'] = "/"
            #logout(request)
            response = HttpResponse(render(request, "ops.html", context))
    else:
        response = HttpResponse(render(request, "home.html"))
    return response

@login_required
def ateams_business(request):
    context = {}
    response = None
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            if st.session.status == Session.RUNNING:
                response = HttpResponse(render(request, "business.html"))
                response.set_cookie('use_ai', st.session.use_ai)
                response.set_cookie('username', request.user.username)
            else:
                if st.session.status == Session.SETUP:
                    context['redir'] = "/setup/"
                elif st.session.status == Session.PRESESSION:
                    context['redir'] = "/presession/"
                elif st.session.status == Session.POSTSESSION:
                    context['redir'] = "/postsession/"
                response = HttpResponse(render(request, "business.html", context))
        else:
            context['redir'] = "/"
            #logout(request)
            response = HttpResponse(render(request, "business.html", context))
    else:
        response = HttpResponse(render(request, "home.html"))
    return response

@login_required
def ateams_postsession(request):
    context = {}
    response = None
    role = None
    st = None
    pos = 0
    team_type = 0
    context['last'] = True
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            if st.session.status == Session.POSTSESSION:
                is_team = True
                # TODO: Make individual/team a property of Structure
                if st.session.structure.name == "Extra":
                    is_team = False
                context['is_team'] = is_team
                next_sessions = Session.objects.filter(session__prior_session=st.session)
                if next_sessions:
                    context['last'] = False
                context['session_ai'] = st.session.use_ai
                up = UserPosition.objects.filter(Q(user=request.user)&Q(session=st.session)).first()
                pos_name = up.position.name
                if "Design Manager" in pos_name:
                    pos = 1
                elif "Design Specialist" in pos_name:
                    pos = 2
                elif "Operations Manager" in pos_name:
                    pos = 3
                elif "Operations Specialist" in pos_name:
                    pos = 4
                elif "Business" in pos_name:
                    pos = 5

                role = up.position.role

                context['role'] = role
                context['position'] = pos

                response = HttpResponse(render(request, "postsession.html", context))
                response.set_cookie('use_ai', st.session.use_ai)
                response.set_cookie('username', request.user.username)
            else:
                if st.session.status == Session.SETUP:
                    context['redir'] = "/setup/"
                elif st.session.status == Session.PRESESSION:
                    context['redir'] = "/presession/"
                elif st.session.status == Session.RUNNING:
                    position = UserPosition.objects.filter(Q(session=st.session)&Q(user=request.user)).first().position
                    if position:
                        if position.role.name == "Business":
                            context['redir'] = "/business/"
                        elif position.role.name == "OpsPlanner":
                            context['redir'] = "/ops/"
                        elif position.role.name == "Designer":
                            context['redir'] = "/design/"
                response = HttpResponse(render(request, "postsession.html", context))
        else:
            context['redir'] = "/"
            #logout(request)
            response = HttpResponse(render(request, "postsession.html", context))
    else:
        response = HttpResponse(render(request, "home.html"))
    return response

@login_required
def ateams_info(request):
    context = {}
    role = None
    st = None
    pos = 0
    team_type = 0
    response = Http404
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            is_team = True
            # TODO: Make individual/team a property of Structure
            if st.session.structure.name == "Extra":
                is_team = False
            context['is_team'] = is_team
            context['state'] = st.session.status
            context['session_ai'] = st.session.use_ai
            context['session'] = st.session.structure.name
            up = UserPosition.objects.filter(Q(user=request.user)&Q(session=st.session)).first()
            pos_name = up.position.name
            if "Design Manager" in pos_name:
                pos = 1
            elif "Design Specialist" in pos_name:
                pos = 2
            elif "Operations Manager" in pos_name:
                pos = 3
            elif "Operations Specialist" in pos_name:
                pos = 4
            elif "Business" in pos_name:
                pos = 5

            role = up.position.role

            context['role'] = role
            context['position'] = pos
            response = HttpResponse(render(request, "info.html", context))
            response.set_cookie('username', request.user.username)
            response.set_cookie('use_ai', st.session.use_ai)
        else:
            response = HttpResponse(render(request, "info.html"))
            response.set_cookie('username', request.user.username)
    else:
        response = Http404
    return response

def ateams_main(request):
    return render(request, "ateams_main.html")
