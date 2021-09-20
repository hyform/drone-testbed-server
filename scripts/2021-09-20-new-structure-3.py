from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

botChannel = Structure.objects.filter(name="Bot 2").first()
if botChannel:
    botChannel.name = "Fall 2021 Bot"
    botChannel.save()