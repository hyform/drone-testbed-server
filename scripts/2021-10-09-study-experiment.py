from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition
from chat.models import Channel, ChannelPosition

organizations = Organization.objects.all()
for organization in organizations:
    if organization.name == "ARL" or organization.name == "PSU" or organization.name == "PSU 2" or organization.name == "CMU" or organization.name == "CMU 2":
        pm_study = Study.objects.create(name="2021 Fall Bot", organization=organization)
        pm_experiment = Experiment.objects.create(name="2021 Fall Bot", study = pm_study)
        pm_experiment_test = Experiment.objects.create(name="2021 Fall Bot Test", study = pm_study)