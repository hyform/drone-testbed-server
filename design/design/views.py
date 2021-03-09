from django.http import HttpResponse, Http404
from django.template import loader
from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Subquery
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from django.utils.safestring import mark_safe
from operator import attrgetter
from exper.models import Role, UserPosition, Structure
from exper.models import Session, SessionTeam, Market
from exper.models import CustomLinks, Exercise
from repo.models import Profile, DesignTeam, Study, Experiment, ExperOrg
import collections
import json
from chat.chat_consumer_listener import ChatConsumerListener
from process.mediation import Interventions
from api.models import SessionTimer
from datetime import datetime


def ateams_homepage(request):
    context = {}
    response = None
    experimenter = False
    if request.user.is_authenticated:
        experimenter = request.user.profile.is_experimenter()
        context['experimenter'] = experimenter
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES) & Q(
            team=request.user.profile.team)).first()
        if st:
            if st.session.status == Session.SETUP:
                context['redir'] = "/setup/"
            elif st.session.status == Session.PRESESSION:
                context['redir'] = "/presession/"
            elif st.session.status == Session.RUNNING:
                position = UserPosition.objects.filter(
                    Q(session=st.session) & Q(user=request.user)).first().position
                if position:
                    if position.role.name == "Business":
                        context['redir'] = "/business/"
                    elif position.role.name == "OpsPlanner":
                        context['redir'] = "/ops/"
                    elif position.role.name == "Designer":
                        context['redir'] = "/design/"
                    elif position.role.name == "Process":
                        context['redir'] = "/process/"
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
    if request.user.is_authenticated and request.user.profile.is_experimenter():
        # If any of these are null, go to the organization page to select them
        if not request.user.profile.organization or not request.user.profile.study or not request.user.profile.experiment:
            context = {}
            orgs = []
            exper_orgs = ExperOrg.objects.filter(user=request.user)
            for exper_org in exper_orgs:
                orgs.append(exper_org.organization)
            context["orgs"] = orgs
            response = HttpResponse(render(request, "organization.html", context))
        else:
            profile = request.user.profile
            organization = None
            study = None
            experiment = None
            org_teams = None
            session_teams = None
            markets = None
            structures = None
            st_dict = {}
            session_next = {}
            all_users = dict()
            exercises = {}
            archived_exercises = {}

            if profile.organization:
                organization = profile.organization
                study = profile.study
                experiment = profile.experiment

                org_teams = DesignTeam.objects.filter(
                    organization=profile.organization)
                for org_team in org_teams:
                    user_profiles = Profile.objects.filter(team=org_team)
                    for user_profile in user_profiles:
                        up_user = user_profile.user
                        user_string = up_user.username + " : " + org_team.name
                        all_users[user_string] = up_user.id
                org_teams_ids = org_teams.values('id')
                session_teams = SessionTeam.objects.filter(team_id__in=org_teams_ids)
                for st in session_teams:
                    st_dict[st.session_id] = DesignTeam.objects.filter(
                        id=st.team_id).first()

                # Note: minus before index means descending order
                current_exercises = Exercise.objects.filter(experiment=experiment).order_by('-id')
                for exercise in current_exercises:
                    exercise_sessions = []
                    sessions = Session.objects.filter(exercise=exercise).order_by('index')
                    all_archived = True
                    session_prev = None
                    for session in sessions:
                        if session_prev:
                            # Keep track of next session for each session
                            session_next[session_prev] = session
                        exercise_sessions.append(session)
                        if session.status != Session.ARCHIVED:
                            # Check if all sessions in exercise are archived
                            all_archived = False
                        session_prev = session
                    # Separate available and archived exercises
                    if all_archived:
                        archived_exercises[exercise] = exercise_sessions
                    else:
                        exercises[exercise] = exercise_sessions

                markets = Market.objects.all()
                structures = Structure.objects.all()

                sorted_all_users = collections.OrderedDict()
                for key, value in sorted(all_users.items()):
                    sorted_all_users[key] = value

            context = {
                'org_teams': org_teams,
                'organization': organization,
                'study': study,
                'experiment': experiment,
                'session_teams': session_teams,
                'st_dict': st_dict,
                'session_next': session_next,
                'markets': markets,
                'structures': structures,
                'all_users': sorted_all_users,
                'exercises': exercises,
                'archived_exercises': archived_exercises
            }
            response = HttpResponse(render(request, "experiment.html", context))
            response.set_cookie('username', request.user.username)
    else:
        response = HttpResponse(render(request, "home.html"))
    return response


@login_required
def ateams_experiment_chat(request):
    if request.user.is_authenticated and request.user.profile.is_experimenter():

        template_sessions = None
        template_sessions = Session.objects.filter(status=Session.TEMPLATE)

        profile = request.user.profile
        org_teams = None
        exp_sessions = None
        session_teams = None
        st_dict = {}
        if profile.organization:
            org_teams = DesignTeam.objects.filter(
                organization=profile.organization)
            org_teams_ids = org_teams.values('id')
            session_teams = SessionTeam.objects.filter(team_id__in=org_teams_ids)
            exp_sessions = Session.objects.filter(Q(id__in=session_teams.values(
                'session_id')) & Q(status__in=Session.ACTIVE_STATES)).order_by('id')
            for st in session_teams:
                st_dict[st.session_id] = DesignTeam.objects.filter(
                    id=st.team_id).first()

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
    else:
        response = HttpResponse(render(request, "home.html"))
    return response


@login_required
def ateams_temp_user_info(request):
    context = {}
    user_info = {}
    if request.user.is_authenticated:
        if request.user.profile and request.user.profile.is_experimenter():
            profile = request.user.profile
            organization = profile.organization
            if organization:
                org_teams = DesignTeam.objects.filter(
                    organization=profile.organization)
                for team in org_teams:
                    user_profiles = Profile.objects.filter(team=team)
                    for user_profile in user_profiles:
                        up_user = user_profile.user
                        if user_profile.is_player():
                            user_info[up_user.username] = user_profile.temp_code
                sorted_user_info = collections.OrderedDict()
                for key, value in sorted(user_info.items()):
                    sorted_user_info[key] = value
                context["user_info"] = sorted_user_info
                return HttpResponse(render(request, "tempuserinfo.html", context))
    return HttpResponse(render(request, "home.html"))


def get_cutsom_links(request, st, context):
    # Get any links which should be displayed to this user
    link_org = None
    link_role = None
    link_structure = None
    link_study = None
    link_experiment = None
    link_position = None
    link_is_team = None
    link_ai = None
    link_status = None
    link_first = None
    link_last = None

    link_org = st.team.organization
    if st.session.exercise:
        if st.session.exercise.experiment:
            link_experiment = st.session.exercise.experiment
            if link_experiment:
                if link_experiment.study:
                    link_study = link_experiment.study
    link_position = position = UserPosition.objects.filter(Q(session=st.session)&Q(user=request.user)).first().position
    link_structure = st.session.structure
    if link_position:
        link_role = position.role
    link_is_team = True
    if st.session.structure.name == "Extra":
        link_is_team = False
    link_ai = st.session.use_ai
    link_status = st.session.status
    num_sessions = Session.objects.filter(exercise=st.session.exercise).count()
    if st.session.index == 1:
        link_first = True
        if st.session.index != num_sessions:
            link_last = False
    elif st.session.index == num_sessions:
        link_first = False
        link_last = True
    else:
        link_first = False
        link_last = False

    custom_links = CustomLinks.objects.filter(
        Q(org__isnull=True) | Q(org=link_org)
        ).filter(
            Q(study__isnull=True) | Q(study=link_study)
        ).filter(
            Q(experiment__isnull=True) | Q(experiment=link_experiment)            
        ).filter(
            Q(role__isnull=True) | Q(role=link_role)
        ).filter(
            Q(structure__isnull=True) | Q(structure=link_structure)
        ).filter(
            Q(position__isnull=True) | Q(position=link_position)
        ).filter(
            Q(is_team__isnull=True) | Q(is_team=link_is_team)
        ).filter(
            Q(ai__isnull=True) | Q(ai=link_ai)
        ).filter(
            Q(status__isnull=True) | Q(status=link_status)
        ).filter(
            Q(first__isnull=True) | Q(first=link_first)
        ).filter(
            Q(last__isnull=True) | Q(last=link_last)
        )

    if custom_links:
        #CustomLinks
        #SURVEY = 1
        #FORM = 2
        #BRIEF = 3
        #TUTORIAL = 4
        survey_links = custom_links.filter(link_type=CustomLinks.SURVEY)
        if survey_links:
            context['survey_links'] = survey_links

        form_links = custom_links.filter(link_type=CustomLinks.FORM)
        if form_links:
            context['form_links'] = form_links

        brief_links = custom_links.filter(link_type=CustomLinks.BRIEF)
        if brief_links:
            context['brief_links'] = brief_links

        tutorial_links = custom_links.filter(link_type=CustomLinks.TUTORIAL)
        if tutorial_links:
            context['tutorial_links'] = tutorial_links

@login_required
def ateams_setup(request):
    context = {}
    response = None
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            get_cutsom_links(request, st, context)

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
                        elif position.role.name == "Process":
                            context['redir'] = "/process/"
                elif st.session.status == Session.POSTSESSION:
                    context['redir'] = "/postsession/"
                response = HttpResponse(render(request, "setup.html", context))
        else:
            context['redir'] = "/"
            # logout(request)
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
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            get_cutsom_links(request, st, context)
            context['session'] = st.session.structure.name
            if st.session.status == Session.PRESESSION:
                is_team = True
                if st.session.structure.name == "Extra":
                    is_team = False
                context['is_team'] = is_team

                num_sessions = Session.objects.filter(exercise=st.session.exercise).count()
                if st.session.index == 1:
                    context['first'] = True
                    if st.session.index != num_sessions:
                        context['last'] = False
                elif st.session.index == num_sessions:
                    context['first'] = False
                    context['last'] = True
                else:
                    context['first'] = False
                    context['last'] = False

                context['session_ai'] = st.session.use_ai
                up = UserPosition.objects.filter(Q(user=request.user)&Q(session=st.session)).first()
                pos_name = up.position.name
                #TODO: some of this can still be removed
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
                        elif position.role.name == "Process":
                            context['redir'] = "/process/"
                elif st.session.status == Session.POSTSESSION:
                    context['redir'] = "/postsession/"
                response = HttpResponse(render(request, "presession.html", context))
        else:
            context['redir'] = "/"
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
            response = HttpResponse(render(request, "business.html", context))
    else:
        response = HttpResponse(render(request, "home.html"))
    return response

@login_required
def ateams_process(request):
    context = {}
    response = None
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            if st.session.status == Session.RUNNING:                                
                context = Interventions.add_intervention_constants(context)                
                response = HttpResponse(render(request, "intervention.html", context))
            else:
                if st.session.status == Session.SETUP:
                    context['redir'] = "/setup/"
                elif st.session.status == Session.PRESESSION:
                    context['redir'] = "/presession/"
                elif st.session.status == Session.POSTSESSION:
                    context['redir'] = "/postsession/"
                context = Interventions.add_intervention_constants(context)
                response = HttpResponse(render(request, "intervention.html", context))
        else:
            context['redir'] = "/"
            context = Interventions.add_intervention_constants(context)
            response = HttpResponse(render(request, "intervention.html", context))
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
    if request.user.is_authenticated:
        st = SessionTeam.objects.filter(Q(session__status__in=Session.ACTIVE_STATES)&Q(team=request.user.profile.team)).first()
        if st:
            get_cutsom_links(request, st, context)
            if st.session.status == Session.POSTSESSION:
                is_team = True
                # TODO: Make individual/team a property of Structure
                if st.session.structure.name == "Extra":
                    is_team = False
                context['is_team'] = is_team

                num_sessions = Session.objects.filter(exercise=st.session.exercise).count()
                if st.session.index == 1:
                    context['first'] = True
                    if st.session.index != num_sessions:
                        context['last'] = False
                elif st.session.index == num_sessions:
                    context['first'] = False
                    context['last'] = True
                else:
                    context['first'] = False
                    context['last'] = False

                context['session_ai'] = st.session.use_ai
                up = UserPosition.objects.filter(Q(user=request.user)&Q(session=st.session)).first()
                #TODO: some of this can still be removed
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

                active_team = st.team
                if active_team:
                    if "cmu team 1" in active_team.name:
                        team_type = 1
                    elif "cmu team 2" in active_team.name:
                        team_type = 1
                    elif "cmu team extra" in active_team.name:
                        team_type = 2
                    elif "psu team 1" in active_team.name:
                        team_type = 10
                    elif "psu team 2" in active_team.name:
                        team_type = 10
                    elif "psu team 5" in active_team.name:
                        team_type = 10
                    elif "psu team 6" in active_team.name:
                        team_type = 10
                    elif "psu extra 1" in active_team.name:
                        team_type = 11
                    elif "psu extra 5" in active_team.name:
                        team_type = 11

                context['role'] = role
                context['position'] = pos
                context['team_type'] = team_type

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
                        elif position.role.name == "Process":
                            context['redir'] = "/process/"
                response = HttpResponse(render(request, "postsession.html", context))
        else:
            context['redir'] = "/"
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
            get_cutsom_links(request, st, context)
            context['state'] = st.session.status

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

@login_required
def structure(request):
    response = HttpResponse(render(request, "structure.html"))
    return response
