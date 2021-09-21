from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

roleBusiness = Role.objects.filter(name="Business").first()
roleOps = Role.objects.filter(name="OpsPlanner").first()
roleDesign = Role.objects.filter(name="Designer").first()

strBot = Structure.objects.filter(name="Fall 2021 Bot").first()
if strBot:
    pos_des_1 = Position.objects.create(name="Design Manager", structure=strBot, role=roleDesign)
    pos_ops_1 = Position.objects.create(name="Operations Manager", structure=strBot, role=roleOps)

    organizations = Organization.objects.all()
    for organization in organizations:
        if organization.name == "ARL" or organization.name == "PSU" or organization.name == "PSU 2" or organization.name == "CMU" or organization.name == "CMU 2":
            CustomLinks.objects.create(
                text="Designer Bot Tutorial",
                link="/static/docs/bot/designbot_tutorial.pdf",
                link_type=4,
                structure=strBot,
                position=pos_des_1
                )

            CustomLinks.objects.create(
                text="Operations Planner Bot Tutorial",
                link="/static/docs/bot/opsbot_tutorial.pdf",
                link_type=4,
                structure=strBot,
                position=pos_ops_1
                )
        