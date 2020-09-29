from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

roleOps = Role.objects.filter(name="OpsPlanner").first()
roleDesign = Role.objects.filter(name="Designer").first()

switchTest = Structure.objects.filter(name="Switch")
if not switchTest:
    structure_switch = Structure.objects.create(name="Switch")
    pos_des_1 = Position.objects.create(name="Design Specialist 1", structure=structure_switch, role=roleDesign)
    pos_des_2 = Position.objects.create(name="Design Specialist 2", structure=structure_switch, role=roleDesign)
    pos_des_3 = Position.objects.create(name="Design Specialist 3", structure=structure_switch, role=roleDesign)
    pos_ops_1 = Position.objects.create(name="Operations Specialist 1", structure=structure_switch, role=roleOps)
    pos_ops_2 = Position.objects.create(name="Operations Specialist 2", structure=structure_switch, role=roleOps)
    pos_ops_3 = Position.objects.create(name="Operations Specialist 3", structure=structure_switch, role=roleOps)

    chan_1 = Channel.objects.create(name="Ops Design 1", structure=structure_switch)
    chan_2 = Channel.objects.create(name="Ops Design 2", structure=structure_switch)
    chan_3 = Channel.objects.create(name="Ops Design 3", structure=structure_switch)

    ChannelPosition.objects.create(channel=chan_1, position=pos_des_1)
    ChannelPosition.objects.create(channel=chan_1, position=pos_ops_1)
    ChannelPosition.objects.create(channel=chan_2, position=pos_des_2)
    ChannelPosition.objects.create(channel=chan_2, position=pos_ops_2)
    ChannelPosition.objects.create(channel=chan_3, position=pos_des_3)
    ChannelPosition.objects.create(channel=chan_3, position=pos_ops_3)

    # All channel currently required for every group
    group_All = Group.objects.create(name="All", structure=structure_switch)
    GroupPosition.objects.create(group=group_All, position=pos_des_1, primary=False)
    GroupPosition.objects.create(group=group_All, position=pos_des_2, primary=False)
    GroupPosition.objects.create(group=group_All, position=pos_des_3, primary=False)
    GroupPosition.objects.create(group=group_All, position=pos_ops_1, primary=False)
    GroupPosition.objects.create(group=group_All, position=pos_ops_2, primary=False)
    GroupPosition.objects.create(group=group_All, position=pos_ops_3, primary=False)

    group_1 = Group.objects.create(name="Ops Design 1", structure=structure_switch)
    GroupPosition.objects.create(group=group_1, position=pos_des_1, primary=True)
    GroupPosition.objects.create(group=group_1, position=pos_ops_1, primary=True)

    group_2 = Group.objects.create(name="Ops Design 2", structure=structure_switch)
    GroupPosition.objects.create(group=group_2, position=pos_des_2, primary=True)
    GroupPosition.objects.create(group=group_2, position=pos_ops_2, primary=True)

    group_3 = Group.objects.create(name="Ops Design 3", structure=structure_switch)
    GroupPosition.objects.create(group=group_3, position=pos_des_3, primary=True)
    GroupPosition.objects.create(group=group_3, position=pos_ops_3, primary=True)

    CustomLinks.objects.create(
        text="Design Specialist Switch",
        link="/static/docs/switch/Design_Specialist_Switch.pdf",
        link_type=3,
        role=roleDesign,
        structure=structure_switch
        )

    CustomLinks.objects.create(
        text="Operations Specialist Switch",
        link="/static/docs/switch/Operations_Specialist_Switch.pdf",
        link_type=3,
        role=roleOps,
        structure=structure_switch
        )

    CustomLinks.objects.create(
        text="Design Tutorial",
        link="/static/docs/designer-tutorial.pdf",
        link_type=4,
        is_team=True,
        ai=True,
        role=roleOps,
        structure=structure_switch
        )

    CustomLinks.objects.create(
        text="Design Tutorial",
        link="/static/docs/designer-tutorial_noAI.pdf",
        link_type=4,
        is_team=True,
        ai=False,
        role=roleOps,
        structure=structure_switch
        )

    CustomLinks.objects.create(
        text="Ops Tutorial",
        link="/static/docs/ops-tutorial.pdf",
        link_type=4,
        ai=True,
        role=roleDesign,
        structure=structure_switch
        )

    CustomLinks.objects.create(
        text="Ops Tutorial",
        link="/static/docs/ops-tutorial_noAI.pdf",
        link_type=4,
        ai=False,
        role=roleDesign,
        structure=structure_switch
        )


noSwitchTest = Structure.objects.filter(name="No Switch")
if not noSwitchTest:
    structure_switch = Structure.objects.create(name="No Switch")
    pos_des_1 = Position.objects.create(name="Design Specialist 1", structure=structure_switch, role=roleDesign)
    pos_des_2 = Position.objects.create(name="Design Specialist 2", structure=structure_switch, role=roleDesign)
    pos_des_3 = Position.objects.create(name="Design Specialist 3", structure=structure_switch, role=roleDesign)
    pos_ops_1 = Position.objects.create(name="Operations Specialist 1", structure=structure_switch, role=roleOps)
    pos_ops_2 = Position.objects.create(name="Operations Specialist 2", structure=structure_switch, role=roleOps)
    pos_ops_3 = Position.objects.create(name="Operations Specialist 3", structure=structure_switch, role=roleOps)
    
    chan_1 = Channel.objects.create(name="Ops Design 1", structure=structure_switch)
    chan_2 = Channel.objects.create(name="Ops Design 2", structure=structure_switch)
    chan_3 = Channel.objects.create(name="Ops Design 3", structure=structure_switch)

    ChannelPosition.objects.create(channel=chan_1, position=pos_des_1)
    ChannelPosition.objects.create(channel=chan_1, position=pos_ops_1)
    ChannelPosition.objects.create(channel=chan_2, position=pos_des_2)
    ChannelPosition.objects.create(channel=chan_2, position=pos_ops_2)
    ChannelPosition.objects.create(channel=chan_3, position=pos_des_3)
    ChannelPosition.objects.create(channel=chan_3, position=pos_ops_3)

    # All channel currently required for every group
    group_All = Group.objects.create(name="All", structure=structure_switch)
    GroupPosition.objects.create(group=group_All, position=pos_des_1, primary=False)
    GroupPosition.objects.create(group=group_All, position=pos_des_2, primary=False)
    GroupPosition.objects.create(group=group_All, position=pos_des_3, primary=False)
    GroupPosition.objects.create(group=group_All, position=pos_ops_1, primary=False)
    GroupPosition.objects.create(group=group_All, position=pos_ops_2, primary=False)
    GroupPosition.objects.create(group=group_All, position=pos_ops_3, primary=False)

    group_1 = Group.objects.create(name="Ops Design 1", structure=structure_switch)
    GroupPosition.objects.create(group=group_1, position=pos_des_1, primary=True)
    GroupPosition.objects.create(group=group_1, position=pos_ops_1, primary=True)

    group_2 = Group.objects.create(name="Ops Design 2", structure=structure_switch)
    GroupPosition.objects.create(group=group_2, position=pos_des_2, primary=True)
    GroupPosition.objects.create(group=group_2, position=pos_ops_2, primary=True)

    group_3 = Group.objects.create(name="Ops Design 3", structure=structure_switch)
    GroupPosition.objects.create(group=group_3, position=pos_des_3, primary=True)
    GroupPosition.objects.create(group=group_3, position=pos_ops_3, primary=True)

    CustomLinks.objects.create(
        text="Design Specialist",
        link="/static/docs/switch/Design_Specialist_NoSwitch.pdf",
        link_type=3,
        role=roleDesign,
        structure=structure_switch
        )

    CustomLinks.objects.create(
        text="Operations Specialist",
        link="/static/docs/switch/Operations_Specialist_NoSwitch.pdf",
        link_type=3,
        role=roleOps,
        structure=structure_switch
        )