from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

roleProcess = Role.objects.filter(name="Process").first()
roleBusiness = Role.objects.filter(name="Business").first()
roleOps = Role.objects.filter(name="OpsPlanner").first()
roleDesign = Role.objects.filter(name="Designer").first()

strProcess = Structure.objects.filter(name="Process Manager").first()
strProcessAI = Structure.objects.filter(name="Process Manager (AI)").first()
strSwitch = Structure.objects.filter(name="Switch").first()
strNoSwitch = Structure.objects.filter(name="No Switch").first()
strExtra = Structure.objects.filter(name="Extra").first()

links_to_fix = CustomLinks.objects.filter(link="/static/docs/process/team_problem_statement_designspecialist.pdf")
for link_to_fix in links_to_fix:
    link_to_fix.is_team = True
    link_to_fix.save()

organizations = Organization.objects.all()
for organization in organizations:
    if organization:
        pm_study = Study.objects.filter(name="2021 Spring Process Manager", organization=organization).first()
        if pm_study:
            CustomLinks.objects.create(
                text="Individual Design Brief",
                link="/static/docs/individual_study.pdf",
                link_type=3,
                is_team=False,
                study=pm_study,
                )