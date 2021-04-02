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
def setup_digital_twin(user_id, unit_structure, market, ai):
    setup_digital_twin_method(user_id, unit_structure, market, ai)

@app.task
def run_digital_twin(session_id, pause_interval):
    print("received run")
    run_digital_twin_method(session_id, pause_interval)

@app.task
def pause_digital_twin(session_id):
    pause_digital_twin_method(session_id)

@app.task
def set_digital_twin_preference(session_id, pref_info):
    result = set_preference_method(session_id, pref_info)

# helpers
def setup_digital_twin_method(user_id, unit_structure, market, ai):
    user = User.objects.filter(id=user_id).first()
    t = AdaptiveTeamAIUpdatedPlanner()
    session = t.setup_session(user, unit_structure, market, ai)


# helpers
def run_digital_twin_method(session_id, pause_interval):
    session = Session.objects.filter(id=session_id).first()
    session_status = session.status
    if session_status == Session.PAUSED:
        session.status = Session.RUNNING
        session.save()
        print("session status updated to running")
    elif session.status != Session.RUNNING:
        t = AdaptiveTeamAIUpdatedPlanner()
        t.setup_with_pause_interval(session, pause_interval)
        print("session started")

def set_preference_method(session_id, pref_info):
    session = Session.objects.filter(id=session_id).first()
    t = AdaptiveTeamAIUpdatedPlanner()
    t.set_preference(session, pref_info)
