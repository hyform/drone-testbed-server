from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

# Update Channels
roleBusiness = Role.objects.filter(name="Business").first()
roleOps = Role.objects.filter(name="OpsPlanner").first()
roleDesign = Role.objects.filter(name="Designer").first()

structureC_a = Structure.objects.filter(name="C").first()
structureC_a.name = "C (All)"
structureC_a.save()

structureC_new = Structure.objects.filter(name="D").first()
structureC_new.name = "C"
structureC_new.save()

structureC_am = Structure.objects.create(name="C (All, Mediation)")
posCbus = Position.objects.create(name="Business Manager", structure=structureC_am, role=roleBusiness)
posCopsman = Position.objects.create(name="Operations Manager", structure=structureC_am, role=roleOps)
posCops1 = Position.objects.create(name="Operations Specialist 1", structure=structureC_am, role=roleOps)
posCops2 = Position.objects.create(name="Operations Specialist 2", structure=structureC_am, role=roleOps)
posCdes1 = Position.objects.create(name="Design Specialist 1", structure=structureC_am, role=roleDesign)
posCdes2 = Position.objects.create(name="Design Specialist 2", structure=structureC_am, role=roleDesign)

chanCbusiness = Channel.objects.create(name="Business", structure=structureC_am)
chanCops = Channel.objects.create(name="Operations", structure=structureC_am)
chanCdesign = Channel.objects.create(name="Design", structure=structureC_am)
chanCall = Channel.objects.create(name="All", structure=structureC_am)

ChannelPosition.objects.create(channel=chanCbusiness, position=posCbus)
ChannelPosition.objects.create(channel=chanCbusiness, position=posCopsman)
ChannelPosition.objects.create(channel=chanCops, position=posCopsman)
ChannelPosition.objects.create(channel=chanCops, position=posCops1)
ChannelPosition.objects.create(channel=chanCops, position=posCops2)
ChannelPosition.objects.create(channel=chanCdesign, position=posCopsman)
ChannelPosition.objects.create(channel=chanCdesign, position=posCdes1)
ChannelPosition.objects.create(channel=chanCdesign, position=posCdes2)
ChannelPosition.objects.create(channel=chanCall, position=posCbus)
ChannelPosition.objects.create(channel=chanCall, position=posCopsman)
ChannelPosition.objects.create(channel=chanCall, position=posCops1)
ChannelPosition.objects.create(channel=chanCall, position=posCops1)
ChannelPosition.objects.create(channel=chanCall, position=posCdes1)
ChannelPosition.objects.create(channel=chanCall, position=posCdes2)

groupC = Group.objects.create(name="All", structure=structureC_am)
GroupPosition.objects.create(group=groupC, position=posCbus, primary=True)
GroupPosition.objects.create(group=groupC, position=posCopsman, primary=True)
GroupPosition.objects.create(group=groupC, position=posCops1, primary=True)
GroupPosition.objects.create(group=groupC, position=posCops2, primary=True)
GroupPosition.objects.create(group=groupC, position=posCdes1, primary=True)
GroupPosition.objects.create(group=groupC, position=posCdes2, primary=True)


structureC_m = Structure.objects.create(name="C (Mediation)")
posDbus = Position.objects.create(name="Business Manager", structure=structureC_m, role=roleBusiness)
posDopsman = Position.objects.create(name="Operations Manager", structure=structureC_m, role=roleOps)
posDops1 = Position.objects.create(name="Operations Specialist 1", structure=structureC_m, role=roleOps)
posDops2 = Position.objects.create(name="Operations Specialist 2", structure=structureC_m, role=roleOps)
posDdes1 = Position.objects.create(name="Design Specialist 1", structure=structureC_m, role=roleDesign)
posDdes2 = Position.objects.create(name="Design Specialist 2", structure=structureC_m, role=roleDesign)

chanDbusiness = Channel.objects.create(name="Business", structure=structureC_m)
chanDops = Channel.objects.create(name="Operations", structure=structureC_m)
chanDdesign = Channel.objects.create(name="Design", structure=structureC_m)

ChannelPosition.objects.create(channel=chanDbusiness, position=posDbus)
ChannelPosition.objects.create(channel=chanDbusiness, position=posDopsman)
ChannelPosition.objects.create(channel=chanDops, position=posDopsman)
ChannelPosition.objects.create(channel=chanDops, position=posDops1)
ChannelPosition.objects.create(channel=chanDops, position=posDops2)
ChannelPosition.objects.create(channel=chanDdesign, position=posDopsman)
ChannelPosition.objects.create(channel=chanDdesign, position=posDdes1)
ChannelPosition.objects.create(channel=chanDdesign, position=posDdes2)

groupD = Group.objects.create(name="All", structure=structureC_m)
GroupPosition.objects.create(group=groupD, position=posDbus, primary=True)
GroupPosition.objects.create(group=groupD, position=posDopsman, primary=True)
GroupPosition.objects.create(group=groupD, position=posDops1, primary=True)
GroupPosition.objects.create(group=groupD, position=posDops2, primary=True)
GroupPosition.objects.create(group=groupD, position=posDdes1, primary=True)
GroupPosition.objects.create(group=groupD, position=posDdes2, primary=True)


# Add links

CustomLinks.objects.create(
    text="Mediation",
    link="/static/docs/Operations_Manager_Mediation_Document.pdf",
    link_type=3,
    structure=structureC_am,
    position=posCopsman
    )

CustomLinks.objects.create(
    text="Mediation",
    link="/static/docs/Operations_Manager_Mediation_Document.pdf",
    link_type=3,
    structure=structureC_m,
    position=posDopsman
    )

psu_org = Organization.objects.filter(name="PSU").first()
if psu_org:
    CustomLinks.objects.create(
        text="Consent form and Pre survey",
        link="https://pennstate.qualtrics.com/jfe/form/SV_8G4uMS7eLrMA5aR",
        link_type=1,
        org=psu_org,
        is_team=True,
        first=True,
        status=7
        )
    
    CustomLinks.objects.create(
        text="Mid Survey",
        link="https://pennstate.qualtrics.com/jfe/form/SV_88IbPByH4w9Tiq9",
        link_type=1,
        org=psu_org,
        is_team=True,
        first=True,
        status=8
        )

    CustomLinks.objects.create(
        text="Post Survey",
        link="https://pennstate.qualtrics.com/jfe/form/SV_afL3OolNmj3DxR3",
        link_type=1,
        org=psu_org,
        is_team=True,
        last=True,
        status=8
        )

    CustomLinks.objects.create(
        text="Consent form and Pre survey",
        link="https://pennstate.qualtrics.com/jfe/form/SV_1EWeb99vWPT0M0B",
        link_type=1,
        org=psu_org,
        is_team=False,
        first=True,
        status=7
        )
    
    CustomLinks.objects.create(
        text="Mid Survey",
        link="https://pennstate.qualtrics.com/jfe/form/SV_1NEsQHcObJ51eyp",
        link_type=1,
        org=psu_org,
        is_team=False,
        first=True,
        status=8
        )

    CustomLinks.objects.create(
        text="Post Survey",
        link="https://pennstate.qualtrics.com/jfe/form/SV_0plaiqCmkaTzdaZ",
        link_type=1,
        org=psu_org,
        is_team=False,
        last=True,
        status=8
        )

    CustomLinks.objects.create(
        text="Design Specialist Problem Statement",
        link="/static/docs/problem_statement_design_specialist.pdf",
        link_type=3,
        position=posCdes1
        )
    
    CustomLinks.objects.create(
        text="Design Specialist Problem Statement",
        link="/static/docs/problem_statement_design_specialist.pdf",
        link_type=3,
        position=posCdes2
        )

    CustomLinks.objects.create(
        text="Operations Manager Problem Statement",
        link="/static/docs/problem_statement_ops_manager.pdf",
        link_type=3,
        position=posCopsman
        )

    CustomLinks.objects.create(
        text="Operations Specialist Problem Statement",
        link="/static/docs/problem_statement_ops_specialist.pdf",
        link_type=3,
        position=posCops1
        )

    CustomLinks.objects.create(
        text="Operations Specialist Problem Statement",
        link="/static/docs/problem_statement_ops_specialist.pdf",
        link_type=3,
        position=posCops2
        )

    CustomLinks.objects.create(
        text="Design Specialist Problem Statement",
        link="/static/docs/problem_statement_design_specialist.pdf",
        link_type=3,
        position=posDdes1
        )
    
    CustomLinks.objects.create(
        text="Design Specialist Problem Statement",
        link="/static/docs/problem_statement_design_specialist.pdf",
        link_type=3,
        position=posDdes2
        )

    CustomLinks.objects.create(
        text="Operations Manager Problem Statement",
        link="/static/docs/problem_statement_ops_manager.pdf",
        link_type=3,
        position=posDopsman
        )

    CustomLinks.objects.create(
        text="Operations Specialist Problem Statement",
        link="/static/docs/problem_statement_ops_specialist.pdf",
        link_type=3,
        position=posDops1
        )

    CustomLinks.objects.create(
        text="Operations Specialist Problem Statement",
        link="/static/docs/problem_statement_ops_specialist.pdf",
        link_type=3,
        position=posDops2
        )

else:
    print("PSU Organization not found")
