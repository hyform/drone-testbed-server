from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

roleProcess = Role.objects.filter(name="Process").first()
roleBusiness = Role.objects.filter(name="Business").first()
roleOps = Role.objects.filter(name="OpsPlanner").first()
roleDesign = Role.objects.filter(name="Designer").first()

strProcess = Structure.objects.filter(name="Process Manager").first()
strProcessAI = Structure.objects.filter(name="Process Manager (AI)").first()
strSwitch = Structure.objects.filter(name="Switch").first()
strNoSwitch = Structure.objects.filter(name="No Switch").first()
strExtra = Structure.objects.filter(name="Extra").first()

organizations = Organization.objects.all()
for organization in organizations:
    if organization.name == "ARL" or organization.name == "PSU" or organization.name == "PSU 2" or organization.name == "CMU" or organization.name == "CMU 2":
        pm_study = Study.objects.filter(name="2021 Spring Process Manager", organization=organization).first()
        if pm_study:

            # Process Manager Structure
            CustomLinks.objects.create(
                text="Consent Form",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_0AR0tmLZX3e6pxk",
                link_type=2,
                study=pm_study,
                status=7,
                first=True,
                structure=strProcess,
                )

            CustomLinks.objects.create(
                text="Post-Study Questionnaire",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_8ogtyVBLDUFdee2",
                link_type=1,
                study=pm_study,
                status=8,
                last=True,
                role=roleDesign,
                structure=strProcess,
                )

            CustomLinks.objects.create(
                text="Post-Study Questionnaire",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_8ogtyVBLDUFdee2",
                link_type=1,
                study=pm_study,
                status=8,
                last=True,
                role=roleOps,
                structure=strProcess,
                )

            CustomLinks.objects.create(
                text="Post-Study Questionnaire",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_8ogtyVBLDUFdee2",
                link_type=1,
                study=pm_study,
                status=8,
                last=True,
                role=roleBusiness,
                structure=strProcess,
                )

            CustomLinks.objects.create(
                text="Post-Study Questionnaire",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_cBmZkJRK7qVSUUS",
                link_type=1,
                study=pm_study,
                status=8,
                last=True,
                role=roleProcess,
                structure=strProcess,
                )

            # Process Manager (AI) Structure
            CustomLinks.objects.create(
                text="Consent Form",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_0AR0tmLZX3e6pxk",
                link_type=2,
                study=pm_study,
                status=7,
                first=True,
                structure=strProcessAI,
                )

            CustomLinks.objects.create(
                text="Post-Study Questionnaire",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_6Gqs6oTuILRtpJQ",
                link_type=1,
                study=pm_study,
                status=8,
                last=True,
                role=roleDesign,
                structure=strProcessAI,
                )

            CustomLinks.objects.create(
                text="Post-Study Questionnaire",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_6Gqs6oTuILRtpJQ",
                link_type=1,
                study=pm_study,
                status=8,
                last=True,
                role=roleOps,
                structure=strProcessAI,
                )

            CustomLinks.objects.create(
                text="Post-Study Questionnaire",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_6Gqs6oTuILRtpJQ",
                link_type=1,
                study=pm_study,
                status=8,
                last=True,
                role=roleBusiness,
                structure=strProcessAI,
                )
