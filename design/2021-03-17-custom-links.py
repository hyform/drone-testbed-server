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
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_8611rduEmKJef6S",
                link_type=2,
                study=pm_study,
                status=7,
                first=True,
                structure=strProcess,
                )

            CustomLinks.objects.create(
                text="Post-Study Survey",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_0diVIADDZWWmyNM",
                link_type=1,
                study=pm_study,
                status=8,
                last=True,
                role=roleDesign,
                structure=strProcess,
                )

            CustomLinks.objects.create(
                text="Post-Study Survey",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_0diVIADDZWWmyNM",
                link_type=1,
                study=pm_study,
                status=8,
                last=True,
                role=roleOps,
                structure=strProcess,
                )

            CustomLinks.objects.create(
                text="Post-Study Survey",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_0diVIADDZWWmyNM",
                link_type=1,
                study=pm_study,
                status=8,
                last=True,
                role=roleBusiness,
                structure=strProcess,
                )

            CustomLinks.objects.create(
                text="Post-Study Survey",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_0Ioyjq4DZF2g2YS",
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
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_8611rduEmKJef6S",
                link_type=2,
                study=pm_study,
                status=7,
                first=True,
                structure=strProcessAI,
                )

            CustomLinks.objects.create(
                text="Post-Study Survey",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_0diVIADDZWWmyNM",
                link_type=1,
                study=pm_study,
                status=8,
                last=True,
                role=roleDesign,
                structure=strProcessAI,
                )

            CustomLinks.objects.create(
                text="Post-Study Survey",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_0diVIADDZWWmyNM",
                link_type=1,
                study=pm_study,
                status=8,
                last=True,
                role=roleOps,
                structure=strProcessAI,
                )

            CustomLinks.objects.create(
                text="Post-Study Survey",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_0diVIADDZWWmyNM",
                link_type=1,
                study=pm_study,
                status=8,
                last=True,
                role=roleBusiness,
                structure=strProcessAI,
                )

            # Extra Structure
            CustomLinks.objects.create(
                text="Consent form and pre-questionnaire",
                link="https://pennstate.qualtrics.com/jfe/form/SV_77oDCrt71khWopo",
                link_type=2,
                study=pm_study,
                status=7,
                first=True,
                structure=strExtra,
                )

            CustomLinks.objects.create(
                text="Mid questionnaire",
                link="https://pennstate.qualtrics.com/jfe/form/SV_diELEEUXFU5xMhw",
                link_type=1,
                study=pm_study,
                status=8,
                first=True,
                structure=strExtra,
                )

            CustomLinks.objects.create(
                text="Post questionnaire",
                link="https://pennstate.qualtrics.com/jfe/form/SV_3gFcV0ByouU7du6",
                link_type=1,
                study=pm_study,
                status=8,
                last=True,
                structure=strExtra,
                )

            # Documents            
            CustomLinks.objects.create(
                text="Design Specialist Problem Statement",
                link="/static/docs/process/team_problem_statement_designspecialist.pdf",
                link_type=3,
                role=roleDesign,
                study=pm_study,
                )

            CustomLinks.objects.create(
                text="Chat Tutorial",
                link="/static/docs/process/chat_tutorial.pdf",
                link_type=4,
                role=roleDesign,
                study=pm_study,
                is_team=True
                )

            CustomLinks.objects.create(
                text="Ops Specialist Problem Statement",
                link="/static/docs/process/team_problem_statement_opsspecialist.pdf",
                link_type=3,
                role=roleOps,
                study=pm_study,
                )

            CustomLinks.objects.create(
                text="Chat Tutorial",
                link="/static/docs/process/chat_tutorial.pdf",
                link_type=4,
                role=roleOps,
                study=pm_study,
                is_team=True
                )

            CustomLinks.objects.create(
                text="Problem Manager Problem Statement",
                link="/static/docs/process/team_problem_statement_problemmanager.pdf",
                link_type=3,
                role=roleBusiness,
                study=pm_study,
                )

            CustomLinks.objects.create(
                text="Chat Tutorial",
                link="/static/docs/process/chat_tutorial.pdf",
                link_type=4,
                role=roleBusiness,
                study=pm_study,
                is_team=True
                )

            CustomLinks.objects.create(
                text="Mediation Tutorial",
                link="/static/docs/process/mediation_tutorial.pdf",
                link_type=4,
                role=roleProcess,
                study=pm_study,
                )

            CustomLinks.objects.create(
                text="Process Manager Problem Statement",
                link="/static/docs/process/team_problem_statement_processmanager.pdf",
                link_type=3,
                role=roleProcess,
                study=pm_study,
                )

        
        # Switch Study
        sw_study = Study.objects.filter(name="2021 Spring Switch", organization=organization).first()
        if sw_study:
            CustomLinks.objects.create(
                text="Consent and Pre-Questionnaire",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_cTiCupnABjaIvm5",
                link_type=2,
                status=7,
                study=sw_study,
                )

            CustomLinks.objects.create(
                text="Post-Questionnaire",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_1LxZCvMNZ8e8nWJ",
                link_type=1,
                status=8,
                study=sw_study,
                is_team=False
                )

            CustomLinks.objects.create(
                text="Post-Questionnaire",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_0DFkAMjdvpLyoLP",
                link_type=1,
                status=8,
                study=sw_study,
                structure=strNoSwitch,
                )

            CustomLinks.objects.create(
                text="Post-Questionnaire",
                link="http://cmu.ca1.qualtrics.com/jfe/form/SV_3EleKTndmrPfa61",
                link_type=1,
                status=8,
                study=sw_study,
                structure=strSwitch,
                )

            CustomLinks.objects.create(
                text="Chat Tutorial",
                link="/static/docs/chat_tutorial.pdf",
                link_type=4,
                study=sw_study,
                is_team=True
                )

            CustomLinks.objects.create(
                text="Design Specialist",
                link="/static/docs/switch/Individual_Study_Switch_Experiment.pdf",
                link_type=4,
                study=sw_study,
                is_team=False
                )








                    