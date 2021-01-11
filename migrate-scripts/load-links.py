from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

# This script loads the document links into the current database
# To run use
# python3 manage.py shell < /vagrant/migrate-scripts/load-links.py

roleBusiness = Role.objects.filter(name="Business").first()
roleOps = Role.objects.filter(name="OpsPlanner").first()
roleDesign = Role.objects.filter(name="Designer").first()

CustomLinks.objects.create(
    text="Business Tutorial",
    link="/static/docs/business_tutorial.pdf",
    link_type=4,
    role=roleBusiness
    )

CustomLinks.objects.create(
    text="Chat Tutorial",
    link="/static/docs/chat_tutorial.pdf",
    link_type=4,
    is_team=True
    )

CustomLinks.objects.create(
    text="Chat Tutorial",
    link="/static/docs/chat_tutorial_individual.pdf",
    link_type=4,
    is_team=False
    )

CustomLinks.objects.create(
    text="Design Tutorial",
    link="/static/docs/designer-tutorial.pdf",
    link_type=4,
    is_team=True,
    ai=True,
    role=roleDesign
    )

CustomLinks.objects.create(
    text="Design Tutorial",
    link="/static/docs/designer-tutorial_individual.pdf",
    link_type=4,
    is_team=False,
    ai=True,
    role=roleDesign
    )

CustomLinks.objects.create(
    text="Design Tutorial",
    link="/static/docs/designer-tutorial_individual_noAI.pdf",
    link_type=4,
    is_team=False,
    ai=False,
    role=roleDesign
    )

CustomLinks.objects.create(
    text="Design Tutorial",
    link="/static/docs/designer-tutorial_noAI.pdf",
    link_type=4,
    is_team=True,
    ai=False,
    role=roleDesign
    )

CustomLinks.objects.create(
    text="Individual Design Brief",
    link="/static/docs/individual_study.pdf",
    link_type=3,
    is_team=False
    )

CustomLinks.objects.create(
    text="Ops Tutorial",
    link="/static/docs/ops-tutorial.pdf",
    link_type=4,
    ai=True,
    role=roleOps
    )

CustomLinks.objects.create(
    text="Ops Tutorial",
    link="/static/docs/ops-tutorial_noAI.pdf",
    link_type=4,
    ai=False,
    role=roleOps
    )

CustomLinks.objects.create(
    text="Business Problem Statement",
    link="/static/docs/problem_statement_business.pdf",
    link_type=3,
    role=roleBusiness
    )

designManager = Position.objects.filter(name__contains="Design Manager")
for dm in designManager:
    CustomLinks.objects.create(
    text="Design Manager Problem Statement",
    link="/static/docs/problem_statement_design_manager.pdf",
    link_type=3,
    position=dm
    )

designSpecialist = Position.objects.filter(name__contains="Design Specialist")
for ds in designSpecialist:
    CustomLinks.objects.create(
    text="Design Specialist Problem Statement",
    link="/static/docs/problem_statement_design_specialist.pdf",
    link_type=3,
    position=ds
    )

opsManager = Position.objects.filter(name__contains="Operations Manager")
for om in opsManager:
    CustomLinks.objects.create(
    text="Operations Manager Problem Statement",
    link="/static/docs/problem_statement_ops_manager.pdf",
    link_type=3,
    position=om
    )

opsSpecialist = Position.objects.filter(name__contains="Operations Specialist")
for os in opsSpecialist:
    CustomLinks.objects.create(
    text="Operations Specialist Problem Statement",
    link="/static/docs/problem_statement_ops_specialist.pdf",
    link_type=3,
    position=os
    )