from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

# Create new Process role
roleProcess = Role.objects.filter(name="Process").first()
if not roleProcess:
    roleProcess =  Role.objects.create(name="Process")

roleBusiness = Role.objects.filter(name="Business").first()
roleOps = Role.objects.filter(name="OpsPlanner").first()
roleDesign = Role.objects.filter(name="Designer").first()

structureTest = Structure.objects.filter(name="Process Manager")
if not structureTest:
    structure_process = Structure.objects.create(name="Process Manager")
    pos_des_1 = Position.objects.create(name="Designer 1", structure=structure_process, role=roleDesign)
    pos_des_2 = Position.objects.create(name="Designer 2", structure=structure_process, role=roleDesign)
    pos_ops_1 = Position.objects.create(name="Ops Planner 1", structure=structure_process, role=roleOps)
    pos_ops_2 = Position.objects.create(name="Ops Planner 2", structure=structure_process, role=roleOps)
    pos_bus = Position.objects.create(name="Problem Manager", structure=structure_process, role=roleBusiness)
    pos_prc = Position.objects.create(name="Process Manager", structure=structure_process, role=roleProcess)

    chan_1 = Channel.objects.create(name="Designer", structure=structure_process)
    chan_2 = Channel.objects.create(name="Operations", structure=structure_process)
    chan_3 = Channel.objects.create(name="Designer Management", structure=structure_process)
    chan_4 = Channel.objects.create(name="Operations Management", structure=structure_process)
    chan_5 = Channel.objects.create(name="Problem Manager", structure=structure_process)

    ChannelPosition.objects.create(channel=chan_1, position=pos_des_1)
    ChannelPosition.objects.create(channel=chan_1, position=pos_des_2)
    ChannelPosition.objects.create(channel=chan_1, position=pos_prc)

    ChannelPosition.objects.create(channel=chan_2, position=pos_ops_1)
    ChannelPosition.objects.create(channel=chan_2, position=pos_ops_2)
    ChannelPosition.objects.create(channel=chan_2, position=pos_prc)

    ChannelPosition.objects.create(channel=chan_3, position=pos_des_1)
    ChannelPosition.objects.create(channel=chan_3, position=pos_des_2)
    ChannelPosition.objects.create(channel=chan_3, position=pos_bus)
    ChannelPosition.objects.create(channel=chan_3, position=pos_prc)

    ChannelPosition.objects.create(channel=chan_4, position=pos_ops_1)
    ChannelPosition.objects.create(channel=chan_4, position=pos_ops_2)
    ChannelPosition.objects.create(channel=chan_4, position=pos_bus)
    ChannelPosition.objects.create(channel=chan_4, position=pos_prc)

    ChannelPosition.objects.create(channel=chan_5, position=pos_bus)
    ChannelPosition.objects.create(channel=chan_5, position=pos_prc)

    # All channel currently required for every group
    group_All = Group.objects.create(name="All", structure=structure_process)
    GroupPosition.objects.create(group=group_All, position=pos_des_1, primary=True)
    GroupPosition.objects.create(group=group_All, position=pos_des_2, primary=True)
    GroupPosition.objects.create(group=group_All, position=pos_ops_1, primary=True)
    GroupPosition.objects.create(group=group_All, position=pos_ops_2, primary=True)
    GroupPosition.objects.create(group=group_All, position=pos_bus, primary=True)
    GroupPosition.objects.create(group=group_All, position=pos_prc, primary=True)

