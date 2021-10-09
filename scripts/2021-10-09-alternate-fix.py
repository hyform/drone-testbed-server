from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

roleBusiness = Role.objects.filter(name="Business").first()
roleOps = Role.objects.filter(name="OpsPlanner").first()
roleDesign = Role.objects.filter(name="Designer").first()

structureTest = Structure.objects.filter(name="Fall 2021 Alternate").first()
if structureTest:
    structureTest.name=("DON'T USE")
    structureTest.save()

structureTest = Structure.objects.filter(name="Fall 2021 Alternate")
if not structureTest:
    structure_process = Structure.objects.create(name="Fall 2021 Alternate")
    pos_des_1 = Position.objects.create(name="Design Specialist 1", structure=structure_process, role=roleDesign)
    pos_des_2 = Position.objects.create(name="Design Specialist 2", structure=structure_process, role=roleDesign)
    pos_ops_1 = Position.objects.create(name="Operations Specialist 1", structure=structure_process, role=roleOps)
    pos_ops_2 = Position.objects.create(name="Operations Specialist 2", structure=structure_process, role=roleOps)
    pos_bus = Position.objects.create(name="Problem Manager", structure=structure_process, role=roleBusiness)

    chan_1 = Channel.objects.create(name="Design 1", structure=structure_process)
    chan_2 = Channel.objects.create(name="Design 2", structure=structure_process)
    chan_3 = Channel.objects.create(name="Operations 1", structure=structure_process)
    chan_4 = Channel.objects.create(name="Operations 2", structure=structure_process)

    ChannelPosition.objects.create(channel=chan_1, position=pos_bus)
    ChannelPosition.objects.create(channel=chan_1, position=pos_des_1)

    ChannelPosition.objects.create(channel=chan_2, position=pos_bus)
    ChannelPosition.objects.create(channel=chan_2, position=pos_des_2)

    ChannelPosition.objects.create(channel=chan_3, position=pos_bus)
    ChannelPosition.objects.create(channel=chan_3, position=pos_ops_1)

    ChannelPosition.objects.create(channel=chan_4, position=pos_bus)
    ChannelPosition.objects.create(channel=chan_4, position=pos_ops_2)

    # All channel currently required for every group
    group_All = Group.objects.create(name="All", structure=structure_process)
    GroupPosition.objects.create(group=group_All, position=pos_des_1, primary=False)
    GroupPosition.objects.create(group=group_All, position=pos_des_2, primary=False)
    GroupPosition.objects.create(group=group_All, position=pos_ops_1, primary=False)
    GroupPosition.objects.create(group=group_All, position=pos_ops_2, primary=False)
    GroupPosition.objects.create(group=group_All, position=pos_bus, primary=True)

    group_design_1 = Group.objects.create(name="Design 1", structure=structure_process)
    GroupPosition.objects.create(group=group_design_1, position=pos_des_1, primary=True)
    GroupPosition.objects.create(group=group_design_1, position=pos_bus, primary=False)

    group_design_2 = Group.objects.create(name="Design 2", structure=structure_process)
    GroupPosition.objects.create(group=group_design_2, position=pos_des_2, primary=True)
    GroupPosition.objects.create(group=group_design_2, position=pos_bus, primary=False)
    
    group_operations_1 = Group.objects.create(name="Operations 1", structure=structure_process)
    GroupPosition.objects.create(group=group_operations_1, position=pos_ops_1, primary=True)
    GroupPosition.objects.create(group=group_operations_1, position=pos_bus, primary=False)

    group_operations_2 = Group.objects.create(name="Operations 2", structure=structure_process)
    GroupPosition.objects.create(group=group_operations_2, position=pos_ops_2, primary=True)
    GroupPosition.objects.create(group=group_operations_2, position=pos_bus, primary=False)
