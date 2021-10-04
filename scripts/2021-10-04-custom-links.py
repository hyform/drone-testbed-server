from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

roleBusiness = Role.objects.filter(name="Business").first()
roleOps = Role.objects.filter(name="OpsPlanner").first()
roleDesign = Role.objects.filter(name="Designer").first()

structure_process = Structure.objects.filter(name="Fall 2021 Bot").first()
pos_bus = Position.objects.filter(structure=structure_process).filter(name="Problem Manager").first()
if pos_bus:
    organizations = Organization.objects.all()
    for organization in organizations:
        if organization.name == "ARL" or organization.name == "PSU" or organization.name == "PSU 2" or organization.name == "CMU" or organization.name == "CMU 2":
            CustomLinks.objects.create(
                text="Problem Manager Bot Tutorial",
                link="/static/docs/bot/businessbot_tutorial.pdf",
                link_type=4,
                structure=structure_process,
                position=pos_bus,
                org=organization
                )
