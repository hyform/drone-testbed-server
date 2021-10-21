from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

roleBusiness = Role.objects.filter(name="Business").first()
roleOps = Role.objects.filter(name="OpsPlanner").first()
roleDesign = Role.objects.filter(name="Designer").first()

bot_structure = Structure.objects.filter(name="Fall 2021 Bot").first()
hum_structure = Structure.objects.filter(name="Fall 2021 Human").first()
alt_structure = Structure.objects.filter(name="Fall 2021 Alternate").first()

if bot_structure:
    CustomLinks.objects.create(
        text="Chat Tutorial",
        link="/static/docs/chat_tutorial.pdf",
        link_type=4,
        structure=bot_structure,
        )

if hum_structure:
    CustomLinks.objects.create(
        text="Chat Tutorial",
        link="/static/docs/chat_tutorial.pdf",
        link_type=4,
        structure=hum_structure,
        )

if alt_structure:
    CustomLinks.objects.create(
        text="Chat Tutorial",
        link="/static/docs/chat_tutorial.pdf",
        link_type=4,
        structure=alt_structure,
        )
