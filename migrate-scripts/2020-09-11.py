from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

# Convert existing profiles to use new user types
user_profiles = Profile.objects.all()
for profile in user_profiles:
    if profile.user.is_superuser == False:
        if profile.user_type == 0:
            if profile.is_exper:
                profile.user_type = Profile.EXPERIMENTER
                profile.save()
            else:
                profile.user_type = Profile.PLAYER
                profile.save()

# Update to new ExperOrg
for profile in user_profiles:
    if profile.is_experimenter():
        exper_orgs = ExperOrg.objects.filter(user=profile.user).filter(organization=profile.organization)
        if not exper_orgs:
            ExperOrg.objects.create(user=profile.user, organization=profile.organization)

# Create Archive Studies for all Organizations and move all current sessions to there
# Also create fall 2020 studies with regular and test experiments
organizations = Organization.objects.all()
for organization in organizations:
    org_studies = Study.objects.filter(organization=organization)
    if not org_studies:
        archive_study = Study.objects.create(name="2020-08 Archive", organization=organization)
        archive_experiment = Experiment.objects.create(name="2020-08 Archive", study = archive_study)
        org_teams = DesignTeam.objects.filter(organization=organization)
        for team in org_teams:
            session_teams = SessionTeam.objects.filter(team=team)
            previous_map = {}
            for session_team in session_teams:
                # This field is going away, but it can help for now
                session_team.session.experiment = archive_experiment
                session_team.session.save()

                if session_team.session.prior_session:
                    previous_map[session_team.session.prior_session] = session_team.session
                else:
                    if session_team.session not in previous_map:
                        previous_map[session_team.session] = None
            for session in previous_map:
                new_exercise = Exercise.objects.create(experiment = archive_experiment)
                session.exercise = new_exercise
                session.index = 1
                session.save()

                second_session = previous_map.get(session)
                if second_session:
                    second_session.exercise = new_exercise
                    second_session.index = 2
                    second_session.save()
        new_study = Study.objects.create(name="2020 Fall", organization=organization)
        new_experiment = Experiment.objects.create(name="2020 Fall", study = new_study)
        new_experiment_test = Experiment.objects.create(name="2020 Fall Test", study = new_study)

# New Structures
structureTest = Structure.objects.filter(name="C")
if not structureTest:
    roleBusiness = Role.objects.filter(name="Business").first()
    roleOps = Role.objects.filter(name="OpsPlanner").first()
    roleDesign = Role.objects.filter(name="Designer").first()

    # Structure C
    structureC = Structure.objects.create(name="C")
    posCbus = Position.objects.create(name="Business Manager", structure=structureC, role=roleBusiness)
    posCopsman = Position.objects.create(name="Operations Manager", structure=structureC, role=roleOps)
    posCops1 = Position.objects.create(name="Operations Specialist 1", structure=structureC, role=roleOps)
    posCops2 = Position.objects.create(name="Operations Specialist 2", structure=structureC, role=roleOps)
    posCdes1 = Position.objects.create(name="Design Specialist 1", structure=structureC, role=roleDesign)
    posCdes2 = Position.objects.create(name="Design Specialist 2", structure=structureC, role=roleDesign)
    
    chanCbusiness = Channel.objects.create(name="Business", structure=structureC)
    chanCops = Channel.objects.create(name="Operations", structure=structureC)
    chanCdesign = Channel.objects.create(name="Design", structure=structureC)
    chanCall = Channel.objects.create(name="All", structure=structureC)

    ChannelPosition.objects.create(channel=chanCbusiness, position=posCbus)
    ChannelPosition.objects.create(channel=chanCbusiness, position=posCopsman)
    ChannelPosition.objects.create(channel=chanCops, position=posCopsman)
    ChannelPosition.objects.create(channel=chanCops, position=posCops1)
    ChannelPosition.objects.create(channel=chanCops, position=posCops2)
    ChannelPosition.objects.create(channel=chanCdesign, position=posCopsman)
    ChannelPosition.objects.create(channel=chanCdesign, position=posCdes1)
    ChannelPosition.objects.create(channel=chanCdesign, position=posCdes2)
    ChannelPosition.objects.create(channel=chanCall, position=posCbus)
    ChannelPosition.objects.create(channel=chanCall, position=posCopsman)
    ChannelPosition.objects.create(channel=chanCall, position=posCops1)
    ChannelPosition.objects.create(channel=chanCall, position=posCops1)
    ChannelPosition.objects.create(channel=chanCall, position=posCdes1)
    ChannelPosition.objects.create(channel=chanCall, position=posCdes2)

    groupC = Group.objects.create(name="All", structure=structureC)
    GroupPosition.objects.create(group=groupC, position=posCbus, primary=True)
    GroupPosition.objects.create(group=groupC, position=posCopsman, primary=True)
    GroupPosition.objects.create(group=groupC, position=posCops1, primary=True)
    GroupPosition.objects.create(group=groupC, position=posCops2, primary=True)
    GroupPosition.objects.create(group=groupC, position=posCdes1, primary=True)
    GroupPosition.objects.create(group=groupC, position=posCdes2, primary=True)

    # Structure D
    structureD = Structure.objects.create(name="D")
    posDbus = Position.objects.create(name="Business Manager", structure=structureD, role=roleBusiness)
    posDopsman = Position.objects.create(name="Operations Manager", structure=structureD, role=roleOps)
    posDops1 = Position.objects.create(name="Operations Specialist 1", structure=structureD, role=roleOps)
    posDops2 = Position.objects.create(name="Operations Specialist 2", structure=structureD, role=roleOps)
    posDdes1 = Position.objects.create(name="Design Specialist 1", structure=structureD, role=roleDesign)
    posDdes2 = Position.objects.create(name="Design Specialist 2", structure=structureD, role=roleDesign)

    chanDbusiness = Channel.objects.create(name="Business", structure=structureD)
    chanDops = Channel.objects.create(name="Operations", structure=structureD)
    chanDdesign = Channel.objects.create(name="Design", structure=structureD)

    ChannelPosition.objects.create(channel=chanDbusiness, position=posDbus)
    ChannelPosition.objects.create(channel=chanDbusiness, position=posDopsman)
    ChannelPosition.objects.create(channel=chanDops, position=posDopsman)
    ChannelPosition.objects.create(channel=chanDops, position=posDops1)
    ChannelPosition.objects.create(channel=chanDops, position=posDops2)
    ChannelPosition.objects.create(channel=chanDdesign, position=posDopsman)
    ChannelPosition.objects.create(channel=chanDdesign, position=posDdes1)
    ChannelPosition.objects.create(channel=chanDdesign, position=posDdes2)

    groupD = Group.objects.create(name="All", structure=structureD)
    GroupPosition.objects.create(group=groupD, position=posDbus, primary=True)
    GroupPosition.objects.create(group=groupD, position=posDopsman, primary=True)
    GroupPosition.objects.create(group=groupD, position=posDops1, primary=True)
    GroupPosition.objects.create(group=groupD, position=posDops2, primary=True)
    GroupPosition.objects.create(group=groupD, position=posDdes1, primary=True)
    GroupPosition.objects.create(group=groupD, position=posDdes2, primary=True)


# Add document links
custom_links = CustomLinks.objects.all()
if not custom_links:
    roleBusiness = Role.objects.filter(name="Business").first()
    roleOps = Role.objects.filter(name="OpsPlanner").first()
    roleDesign = Role.objects.filter(name="Designer").first()

    CustomLinks.objects.create(
        text="Business Tutorial",
        link="/static/docs/business_tutorial.pdf",
        link_type=4,
        role=roleBusiness
        )
    
    CustomLinks.objects.create(
        text="Chat Tutorial",
        link="/static/docs/chat_tutorial.pdf",
        link_type=4,
        is_team=True
        )

    CustomLinks.objects.create(
        text="Chat Tutorial",
        link="/static/docs/chat_tutorial_individual.pdf",
        link_type=4,
        is_team=False
        )

    CustomLinks.objects.create(
        text="Design Tutorial",
        link="/static/docs/designer-tutorial.pdf",
        link_type=4,
        is_team=True,
        ai=True,
        role=roleDesign
        )

    CustomLinks.objects.create(
        text="Design Tutorial",
        link="/static/docs/designer-tutorial_individual.pdf",
        link_type=4,
        is_team=False,
        ai=True,
        role=roleDesign
        )

    CustomLinks.objects.create(
        text="Design Tutorial",
        link="/static/docs/designer-tutorial_individual_noAI.pdf",
        link_type=4,
        is_team=False,
        ai=False,
        role=roleDesign
        )

    CustomLinks.objects.create(
        text="Design Tutorial",
        link="/static/docs/designer-tutorial_noAI.pdf",
        link_type=4,
        is_team=True,
        ai=False,
        role=roleDesign
        )

    CustomLinks.objects.create(
        text="Individual Design Brief",
        link="/static/docs/individual_study.pdf",
        link_type=3,
        is_team=False
        )

    CustomLinks.objects.create(
        text="Ops Tutorial",
        link="/static/docs/ops-tutorial.pdf",
        link_type=4,
        ai=True,
        role=roleOps
        )

    CustomLinks.objects.create(
        text="Ops Tutorial",
        link="/static/docs/ops-tutorial_noAI.pdf",
        link_type=4,
        ai=False,
        role=roleOps
        )

    CustomLinks.objects.create(
        text="Business Problem Statement",
        link="/static/docs/problem_statement_business.pdf",
        link_type=3,
        role=roleBusiness
        )
    
    designManager = Position.objects.filter(name__contains="Design Manager")
    for dm in designManager:
        CustomLinks.objects.create(
        text="Design Manager Problem Statement",
        link="/static/docs/problem_statement_design_manager.pdf",
        link_type=3,
        position=dm
        )

    designSpecialist = Position.objects.filter(name__contains="Design Specialist")
    for ds in designSpecialist:
        CustomLinks.objects.create(
        text="Design Specialist Problem Statement",
        link="/static/docs/problem_statement_design_specialist.pdf",
        link_type=3,
        position=ds
        )

    opsManager = Position.objects.filter(name__contains="Operations Manager")
    for om in opsManager:
        CustomLinks.objects.create(
        text="Operations Manager Problem Statement",
        link="/static/docs/problem_statement_ops_manager.pdf",
        link_type=3,
        position=om
        )

    opsSpecialist = Position.objects.filter(name__contains="Operations Specialist")
    for os in opsSpecialist:
        CustomLinks.objects.create(
        text="Operations Specialist Problem Statement",
        link="/static/docs/problem_statement_ops_specialist.pdf",
        link_type=3,
        position=os
        )

dronebot = Channel.objects.filter(name="DroneBot")
if not dronebot:
    Channel.objects.create(name="DroneBot")