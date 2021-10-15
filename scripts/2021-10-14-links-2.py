from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

roleBusiness = Role.objects.filter(name="Business").first()
roleOps = Role.objects.filter(name="OpsPlanner").first()
roleDesign = Role.objects.filter(name="Designer").first()

strBot = Structure.objects.filter(name="Fall 2021 Bot").first()
if strBot:
    
    CustomLinks.objects.create(
        text="Designer Bot Tutorial (Video)",
        link="/static/docs/bot/designbot_tutorial.mp4",
        link_type=4,
        structure=strBot,
        role=roleDesign
        )

    CustomLinks.objects.create(
        text="Operations Planner Bot Tutorial (Video)",
        link="/static/docs/bot/opsbot_tutorial.mp4",
        link_type=4,
        structure=strBot,
        role=roleOps
        )

    CustomLinks.objects.create(
        text="Problem Manager Bot Tutorial (Video)",
        link="/static/docs/bot/businessbot_tutorial.mp4",
        link_type=4,
        structure=strBot,
        role=roleBusiness
        )