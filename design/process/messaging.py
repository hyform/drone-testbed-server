from django.contrib.auth.models import User
from django.db.models import Q, Subquery
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from chat.models import Channel, Message
from exper.models import UserPosition, GroupPosition, Position, Session, Structure
from repo.models import DataLog
from .mediation import Interventions

def send_helper(channed_id, session_id, intervention): 
    instance = str(channed_id) + "___" + str(session_id)
    async_to_sync(get_channel_layer().group_send)(
        instance,
        {
            'type': 'chat.message',
            'message': intervention,
            'sender': "Process Manager",
            'channel': instance
        }
    )

# num is 1 to 13
def send_intervention(num, session_id):
    session = Session.objects.filter(id=session_id).first()
    structure = session.structure
    if structure.name == "Process Manager" or structure.name == "Process Manager (AI)":
        channels = Channel.objects.filter(structure=structure)

        designerChannel = channels.filter(name="Designer").first()
        operationsChannel = channels.filter(name="Operations").first()
        designerManagementChannel = channels.filter(name="Designer Management").first()
        operationsManagementChannel = channels.filter(name="Operations Management").first()
        problemManagerChannel = channels.filter(name="Problem Manager").first()

        if str(num) == str(1):
            send_helper(operationsChannel.id, session_id, Interventions.ACTION_1)
        elif str(num) == str(2):
            send_helper(operationsChannel.id, session_id, Interventions.ACTION_2)
        elif str(num) == str(3):
            send_helper(operationsChannel.id, session_id, Interventions.ACTION_3) 
        elif str(num) == str(4):
            send_helper(designerChannel.id, session_id, Interventions.ACTION_4)
        elif str(num) == str(5):
            send_helper(designerChannel.id, session_id, Interventions.ACTION_5)            
        elif str(num) == str(6):
            send_helper(designerChannel.id, session_id, Interventions.ACTION_6)
        elif str(num) == str(7):
            send_helper(designerChannel.id, session_id, Interventions.COMMUNICATION_1)
            send_helper(operationsChannel.id, session_id, Interventions.COMMUNICATION_1)
            send_helper(problemManagerChannel.id, session_id, Interventions.COMMUNICATION_1)
        elif str(num) == str(8):
            send_helper(designerChannel.id, session_id, Interventions.COMMUNICATION_2)
            send_helper(operationsChannel.id, session_id, Interventions.COMMUNICATION_2)
            send_helper(problemManagerChannel.id, session_id, Interventions.COMMUNICATION_2)
        elif str(num) == str(9):
            send_helper(designerChannel.id, session_id, Interventions.COMMUNICATION_3)
            send_helper(operationsChannel.id, session_id, Interventions.COMMUNICATION_3)
            send_helper(problemManagerChannel.id, session_id, Interventions.COMMUNICATION_3)
        elif str(num) == str(10):
            send_helper(operationsChannel.id, session_id, Interventions.COMMUNICATION_4)
        elif str(num) == str(11):
            send_helper(designerChannel.id, session_id, Interventions.COMMUNICATION_5)
        elif str(num) == str(12):
            send_helper(problemManagerChannel.id, session_id, Interventions.COMMUNICATION_6)
        elif str(num) == str(13):
            # No intervention sent
            # TODO: log no intervention was sent
            pass
        else:
            # Unexpected value
            pass
