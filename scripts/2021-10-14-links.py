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

bot_design_manager = Position.objects.filter(structure=bot_structure).filter(name="Design Manager").first()
if bot_design_manager:
    bot_design_manager.name = "Design Specialist 1"
    bot_design_manager.save()
bot_design_specialist = Position.objects.filter(structure=bot_structure).filter(name="Design Specialist").first()
if bot_design_specialist:
    bot_design_specialist.name = "Design Specialist 2"
    bot_design_specialist.save()

bot_operations_manager = Position.objects.filter(structure=bot_structure).filter(name="Operations Manager").first()
if bot_operations_manager:
    bot_operations_manager.name = "Operations Specialist 1"
    bot_operations_manager.save()
bot_operations_specialist = Position.objects.filter(structure=bot_structure).filter(name="Operations Specialist").first()
if bot_operations_specialist:
    bot_operations_specialist.name = "Operations Specialist 2"
    bot_operations_specialist.save()

hum_design_manager = Position.objects.filter(structure=hum_structure).filter(name="Design Manager").first()
if hum_design_manager:
    hum_design_manager.name = "Design Specialist 1"
    hum_design_manager.save()
hum_design_specialist = Position.objects.filter(structure=hum_structure).filter(name="Design Specialist").first()
if hum_design_specialist:
    hum_design_specialist.name = "Design Specialist 2"
    hum_design_specialist.save()

hum_operations_manager = Position.objects.filter(structure=hum_structure).filter(name="Operations Manager").first()
if hum_operations_manager:
    hum_operations_manager.name = "Operations Specialist 1"
    hum_operations_manager.save()
hum_operations_specialist = Position.objects.filter(structure=hum_structure).filter(name="Operations Specialist").first()
if hum_operations_specialist:
    hum_operations_specialist.name = "Operations Specialist 2"
    hum_operations_specialist.save()

CustomLinks.objects.create(
    text="Problem Statement",
    link="/static/docs/bot/problem_statement/Problem_statement_designspecialist_BOT.pdf",
    link_type=3,    
    role=roleDesign,
    structure=bot_structure,
    in_tutorial=False
    )

CustomLinks.objects.create(
    text="Problem Statement",
    link="/static/docs/bot/problem_statement/Problem_statement_opsspecialist_BOT.pdf",
    link_type=3,    
    role=roleOps,
    structure=bot_structure,
    in_tutorial=False
    )

CustomLinks.objects.create(
    text="Problem Statement",
    link="/static/docs/bot/problem_statement/Problem_statement_problem_manager_BOT.pdf",
    link_type=3,    
    role=roleBusiness,
    structure=bot_structure,
    in_tutorial=False
    )

CustomLinks.objects.create(
    text="Problem Statement",
    link="/static/docs/bot/problem_statement/Problem_statement_design_specialist_human.pdf",
    link_type=3,    
    role=roleDesign,
    structure=hum_structure,
    in_tutorial=False
    )

CustomLinks.objects.create(
    text="Problem Statement",
    link="/static/docs/bot/problem_statement/Problem_statement_ops_specialist_human.pdf",
    link_type=3,    
    role=roleOps,
    structure=hum_structure,
    in_tutorial=False
    )

CustomLinks.objects.create(
    text="Problem Statement",
    link="/static/docs/bot/problem_statement/Problem_statement_problem_manager_Human.pdf",
    link_type=3,    
    role=roleBusiness,
    structure=hum_structure,
    in_tutorial=False
    )

CustomLinks.objects.create(
    text="Problem Statement",
    link="/static/docs/bot/problem_statement/Problem_statement_design_specialist_alternate.pdf",
    link_type=3,    
    role=roleDesign,
    structure=alt_structure,
    in_tutorial=False
    )

CustomLinks.objects.create(
    text="Problem Statement",
    link="/static/docs/bot/problem_statement/Problem_statement_ops_specialist_alternate.pdf",
    link_type=3,    
    role=roleOps,
    structure=alt_structure,
    in_tutorial=False
    )

CustomLinks.objects.create(
    text="Problem Statement",
    link="/static/docs/bot/problem_statement/Problem_statement_problem_manager_alternate.pdf",
    link_type=3,    
    role=roleBusiness,
    structure=alt_structure,
    in_tutorial=False
    )

