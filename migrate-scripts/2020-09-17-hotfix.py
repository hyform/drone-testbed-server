from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

roleOps = Role.objects.filter(name="OpsPlanner").first()

print("Checking C (All)")
structureC_a = Structure.objects.filter(name="C (All)").first()
chanCall_a = Channel.objects.filter(name="All").filter(structure=structureC_a).first()
posCops1_a = Position.objects.filter(name="Operations Specialist 1").filter(structure=structureC_a).filter(role=roleOps).first()
posCops2_a = Position.objects.filter(name="Operations Specialist 2").filter(structure=structureC_a).filter(role=roleOps).first()
a_positions = ChannelPosition.objects.filter(channel=chanCall_a).filter(position=posCops1_a)
if a_positions.count() == 2:    
    print("Found 2 entries, fixing")
    chpo = a_positions.first()
    chpo.position = posCops2_a
    chpo.save()
else:
    print("Did not find 2 entries")

print("Checking C (All, Mediation)")
structureC_am = Structure.objects.filter(name="C (All, Mediation)").first()
chanCall_am = Channel.objects.filter(name="All").filter(structure=structureC_am).first()
posCops1_am = Position.objects.filter(name="Operations Specialist 1").filter(structure=structureC_am).filter(role=roleOps).first()
posCops2_am = Position.objects.filter(name="Operations Specialist 2").filter(structure=structureC_am).filter(role=roleOps).first()
am_positions = ChannelPosition.objects.filter(channel=chanCall_am).filter(position=posCops1_am)
if am_positions.count() == 2:
    print("Found 2 entries, fixing")
    chpo = am_positions.first()
    chpo.position = posCops2_am
    chpo.save()
else:
    print("Did not find 2 entries")
