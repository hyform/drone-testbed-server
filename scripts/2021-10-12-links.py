from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

roleBusiness = Role.objects.filter(name="Business").first()
roleOps = Role.objects.filter(name="OpsPlanner").first()
roleDesign = Role.objects.filter(name="Designer").first()

organizations = Organization.objects.all()
for organization in organizations:
    if organization.name == "ARL" or organization.name == "PSU" or organization.name == "PSU 2" or organization.name == "CMU" or organization.name == "CMU 2":
        bot_study = Study.objects.filter(name="2021 Fall Bot", organization=organization).first()
        if bot_study:

            #Teams
            CustomLinks.objects.create(
                text="Consent Form",
                link="https://pennstate.qualtrics.com/jfe/form/SV_3VJZdSgBK3ZO24S",
                link_type=1,
                study=bot_study,
                status=7,
                first=True,
                is_team=True,
                )
            
            CustomLinks.objects.create(
                text="Pre-experiment Questionnaire",
                link="https://pennstate.qualtrics.com/jfe/form/SV_eKcnkKLs6RPPBFs",
                link_type=1,
                study=bot_study,
                status=7,
                first=True,
                is_team=True,
                )

            CustomLinks.objects.create(
                text="Mid-experiment Questionnaire",
                link="https://pennstate.qualtrics.com/jfe/form/SV_6rQv76hypG6n5dQ",
                link_type=1,
                study=bot_study,
                status=7,
                last=True,
                is_team=True,
                )
            
            CustomLinks.objects.create(
                text="Post-experiment Questionnaire",
                link="https://pennstate.qualtrics.com/jfe/form/SV_dbrtgRoSAHKMzHw",
                link_type=1,
                study=bot_study,
                status=8,
                last=True,
                is_team=True,
                )

            #Individual
            CustomLinks.objects.create(
                text="Consent Form",
                link="https://pennstate.qualtrics.com/jfe/form/SV_0kPvFaepO3Vrb6u",
                link_type=1,
                study=bot_study,
                status=7,
                first=True,
                is_team=False,
                )
            
            CustomLinks.objects.create(
                text="Pre-experiment Questionnaire",
                link="https://pennstate.qualtrics.com/jfe/form/SV_6spve0dRsbCo8WG",
                link_type=1,
                study=bot_study,
                status=7,
                first=True,
                is_team=False,
                )

            CustomLinks.objects.create(
                text="Mid-experiment Questionnaire",
                link="https://pennstate.qualtrics.com/jfe/form/SV_3drLtwITXvdrvpQ",
                link_type=1,
                study=bot_study,
                status=7,
                last=True,
                is_team=False,
                )
            
            CustomLinks.objects.create(
                text="Post-experiment Questionnaire",
                link="https://pennstate.qualtrics.com/jfe/form/SV_3jwoRWynweZflMa",
                link_type=1,
                study=bot_study,
                status=8,
                last=True,
                is_team=False,
                )

