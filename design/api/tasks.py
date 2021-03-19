from celery import Celery
from celery import shared_task
from celery.utils.log import get_task_logger
from exper.models import UserPosition, Session, User
from exper.models import DigitalTwin
from ai.agents.adaptive_team_ai_updated_planner import AdaptiveTeamAIUpdatedPlanner
from exper.serializers import DigitalTwinSerializer
from design.celery import app


#@celery.task
#@shared_task
@app.task
def run_digital_twin(user_id, unit_structure, market, ai):
    result = run_digital_twin_method(user_id, unit_structure, market, ai)


# helpers
def run_digital_twin_method(user_id, unit_structure, market, ai):
    user = User.objects.filter(id=user_id).first()
    t = AdaptiveTeamAIUpdatedPlanner()
    session = t.setup_session(user, unit_structure, market, ai)
    t.setup(session)
    return "works"


def get_digital_twin_for_session(session_id):
    session_user_positions = []
    user_positions = UserPosition.objects.all()     # for some reason , filter does not work, fix this
    for user in user_positions:
        if user.session.id == session_id:
            session_user_positions.append(user)

    digital_twin_setups = []
    # query or create digital twin objects
    for user in session_user_positions:
        digital_twin_setup = DigitalTwin.objects.filter(user_position=user)
        if len(digital_twin_setup) == 0:
            new_setup = DigitalTwin.objects.create(user_position=user)
            new_setup.save()
            digital_twin_setups.append(new_setup)
        else:
            digital_twin_setups.append(digital_twin_setup[0])

    return digital_twin_setups
