from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

roleProcess = Role.objects.filter(name="Process").first()
roleBusiness = Role.objects.filter(name="Business").first()
roleOps = Role.objects.filter(name="OpsPlanner").first()
roleDesign = Role.objects.filter(name="Designer").first()

structureTest = Structure.objects.filter(name="Process Manager (AI)")
if not structureTest:
    structure_process = Structure.objects.create(name="Process Manager (AI)")
    pos_des_1 = Position.objects.create(name="Designer 1", structure=structure_process, role=roleDesign)
    pos_des_2 = Position.objects.create(name="Designer 2", structure=structure_process, role=roleDesign)
    pos_ops_1 = Position.objects.create(name="Ops Planner 1", structure=structure_process, role=roleOps)
    pos_ops_2 = Position.objects.create(name="Ops Planner 2", structure=structure_process, role=roleOps)
    pos_bus = Position.objects.create(name="Problem Manager", structure=structure_process, role=roleBusiness)

    chan_1 = Channel.objects.create(name="Designer", structure=structure_process)
    chan_2 = Channel.objects.create(name="Operations", structure=structure_process)
    chan_3 = Channel.objects.create(name="Designer Management", structure=structure_process)
    chan_4 = Channel.objects.create(name="Operations Management", structure=structure_process)
    chan_5 = Channel.objects.create(name="Problem Manager", structure=structure_process)

    ChannelPosition.objects.create(channel=chan_1, position=pos_des_1)
    ChannelPosition.objects.create(channel=chan_1, position=pos_des_2)

    ChannelPosition.objects.create(channel=chan_2, position=pos_ops_1)
    ChannelPosition.objects.create(channel=chan_2, position=pos_ops_2)

    ChannelPosition.objects.create(channel=chan_3, position=pos_des_1)
    ChannelPosition.objects.create(channel=chan_3, position=pos_des_2)
    ChannelPosition.objects.create(channel=chan_3, position=pos_bus)

    ChannelPosition.objects.create(channel=chan_4, position=pos_ops_1)
    ChannelPosition.objects.create(channel=chan_4, position=pos_ops_2)
    ChannelPosition.objects.create(channel=chan_4, position=pos_bus)

    ChannelPosition.objects.create(channel=chan_5, position=pos_bus)

    # All channel currently required for every group
    group_All = Group.objects.create(name="All", structure=structure_process)
    GroupPosition.objects.create(group=group_All, position=pos_des_1, primary=True)
    GroupPosition.objects.create(group=group_All, position=pos_des_2, primary=True)
    GroupPosition.objects.create(group=group_All, position=pos_ops_1, primary=True)
    GroupPosition.objects.create(group=group_All, position=pos_ops_2, primary=True)
    GroupPosition.objects.create(group=group_All, position=pos_bus, primary=True)

organizations = Organization.objects.all()
for organization in organizations:
    if organization.name == "ARL" or organization.name == "PSU" or organization.name == "PSU 2" or organization.name == "CMU" or organization.name == "CMU 2":
        pm_study = Study.objects.create(name="2021 Spring Process Manager", organization=organization)
        pm_experiment = Experiment.objects.create(name="2021 Spring Process Manager", study = pm_study)
        pm_experiment_test = Experiment.objects.create(name="2021 Spring Process Manager Test", study = pm_study)

        CustomLinks.objects.create(
            text="Mediation Tutorial",
            link="/static/docs/process/mediation_tutorial.pdf",
            link_type=4,
            role=roleProcess,
            study=pm_study,
            )

        CustomLinks.objects.create(
            text="Design Specialist Problem Statement",
            link="/static/docs/process/team_problem_statement_designspecialist.pdf",
            link_type=3,
            role=roleDesign,
            study=pm_study,
            )

        CustomLinks.objects.create(
            text="Ops Specialist Problem Statement",
            link="/static/docs/process/team_problem_statement_opsspecialist.pdf",
            link_type=3,
            role=roleOps,
            study=pm_study,
            )

        CustomLinks.objects.create(
            text="Problem Manager Problem Statement",
            link="/static/docs/process/team_problem_statement_problemmanager.pdf",
            link_type=3,
            role=roleBusiness,
            study=pm_study,
            )

        CustomLinks.objects.create(
            text="Process Manager Problem Statement",
            link="/static/docs/process/team_problem_statement_processmanager.pdf",
            link_type=3,
            role=roleProcess,
            study=pm_study,
            )

        CustomLinks.objects.create(
            text="Consent Form",
            link="http://cmu.ca1.qualtrics.com/jfe/form/SV_8611rduEmKJef6S",
            link_type=2,
            study=pm_study,
            status=7,
            first=True,
            )

        CustomLinks.objects.create(
            text="Pre-Study Survey",
            link="http://cmu.ca1.qualtrics.com/jfe/form/SV_bw0YX0n8Vl7bAYS",
            link_type=1,
            study=pm_study,
            status=7,
            first=True,
            )

        CustomLinks.objects.create(
            text="Post-Study Survey",
            link="http://cmu.ca1.qualtrics.com/jfe/form/SV_0diVIADDZWWmyNM",
            link_type=1,
            study=pm_study,
            status=8,
            last=True,
            role=roleDesign,
            )

        CustomLinks.objects.create(
            text="Post-Study Survey",
            link="http://cmu.ca1.qualtrics.com/jfe/form/SV_0diVIADDZWWmyNM",
            link_type=1,
            study=pm_study,
            status=8,
            last=True,
            role=roleOps,
            )

        CustomLinks.objects.create(
            text="Post-Study Survey",
            link="http://cmu.ca1.qualtrics.com/jfe/form/SV_0diVIADDZWWmyNM",
            link_type=1,
            study=pm_study,
            status=8,
            last=True,
            role=roleBusiness,
            )

        CustomLinks.objects.create(
            text="Post-Study Survey",
            link="http://cmu.ca1.qualtrics.com/jfe/form/SV_0Ioyjq4DZF2g2YS",
            link_type=1,
            study=pm_study,
            status=8,
            last=True,
            role=roleProcess,
            )

        sw_study = Study.objects.create(name="2021 Spring Switch", organization=organization)
        sw_experiment = Experiment.objects.create(name="2021 Spring Switch", study = sw_study)
        sw_experiment_test = Experiment.objects.create(name="2021 Spring Switch Test", study = sw_study)

