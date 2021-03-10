from django.contrib.auth.models import User
from django.db.models import Q, Subquery
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from chat.models import Channel, Message
from exper.models import UserPosition, GroupPosition, Position, Session, Structure
from repo.models import DataLog
from .mediation import Interventions


# num is 1 to 13
def send_intervention(num, session_id):
    structure = Structure.objects.filter(name="Process Manager").first()
    if structure:
        channels = Channel.objects.filter(structure=structure)

        designerChannel = channels.filter(name="Designer").first()
        operationsChannel = channels.filter(name="Operations").first()
        designerManagementChannel = channels.filter(name="Designer Management").first()
        operationsManagementChannel = channels.filter(name="Operations Management").first()
        problemManagerChannel = channels.filter(name="Problem Manager").first()

        if str(num) == str(1):
            instance = str(operationsChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance,
                {
                    'type': 'chat.message',
                    'message': Interventions.ACTION_1,
                    'sender': "Process Manager",
                    'channel': instance
                }
            )
        elif str(num) == str(2):
            instance = str(operationsChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance,
                {
                    'type': 'chat.message',
                    'message': Interventions.ACTION_2,
                    'sender': "Process Manager",
                    'channel': instance
                }
            )
        elif str(num) == str(3):
            instance = str(operationsChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance,
                {
                    'type': 'chat.message',
                    'message': Interventions.ACTION_3,
                    'sender': "Process Manager",
                    'channel': instance
                }
            )
        elif str(num) == str(4):
            instance = str(designerChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance,
                {
                    'type': 'chat.message',
                    'message': Interventions.ACTION_4,
                    'sender': "Process Manager",
                    'channel': instance
                }
            )
        elif str(num) == str(5):
            instance = str(designerChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance,
                {
                    'type': 'chat.message',
                    'message': Interventions.ACTION_5,
                    'sender': "Process Manager",
                    'channel': instance
                }
            )
        elif str(num) == str(6):
            instance = str(designerChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance,
                {
                    'type': 'chat.message',
                    'message': Interventions.ACTION_6,
                    'sender': "Process Manager",
                    'channel': instance
                }
            )
        elif str(num) == str(7):
            instance = str(designerChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance,
                {
                    'type': 'chat.message',
                    'message': Interventions.COMMUNICATION_1,
                    'sender': "Process Manager",
                    'channel': instance
                }
            )

            instance2 = str(operationsChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance2,
                {
                    'type': 'chat.message',
                    'message': Interventions.COMMUNICATION_1,
                    'sender': "Process Manager",
                    'channel': instance2
                }
            )

            instance3 = str(problemManagerChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance3,
                {
                    'type': 'chat.message',
                    'message': Interventions.COMMUNICATION_1,
                    'sender': "Process Manager",
                    'channel': instance3
                }
            )
        elif str(num) == str(8):
            instance = str(designerChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance,
                {
                    'type': 'chat.message',
                    'message': Interventions.COMMUNICATION_2,
                    'sender': "Process Manager",
                    'channel': instance
                }
            )

            instance2 = str(operationsChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance2,
                {
                    'type': 'chat.message',
                    'message': Interventions.COMMUNICATION_2,
                    'sender': "Process Manager",
                    'channel': instance2
                }
            )

            instance3 = str(problemManagerChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance3,
                {
                    'type': 'chat.message',
                    'message': Interventions.COMMUNICATION_2,
                    'sender': "Process Manager",
                    'channel': instance3
                }
            )
        elif str(num) == str(9):
            instance = str(designerChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance,
                {
                    'type': 'chat.message',
                    'message': Interventions.COMMUNICATION_3,
                    'sender': "Process Manager",
                    'channel': instance
                }
            )

            instance2 = str(operationsChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance2,
                {
                    'type': 'chat.message',
                    'message': Interventions.COMMUNICATION_3,
                    'sender': "Process Manager",
                    'channel': instance2
                }
            )

            instance3 = str(problemManagerChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance3,
                {
                    'type': 'chat.message',
                    'message': Interventions.COMMUNICATION_3,
                    'sender': "Process Manager",
                    'channel': instance3
                }
            )
        elif str(num) == str(10):
            instance = str(operationsChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance,
                {
                    'type': 'chat.message',
                    'message': Interventions.COMMUNICATION_4,
                    'sender': "Process Manager",
                    'channel': instance
                }
            )
        elif str(num) == str(11):
            instance = str(designerChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance,
                {
                    'type': 'chat.message',
                    'message': Interventions.COMMUNICATION_5,
                    'sender': "Process Manager",
                    'channel': instance
                }
            )
        elif str(num) == str(12):
            instance = str(problemManagerChannel.id) + "___" + str(session_id)
            async_to_sync(get_channel_layer().group_send)(
                instance,
                {
                    'type': 'chat.message',
                    'message': Interventions.COMMUNICATION_6,
                    'sender': "Process Manager",
                    'channel': instance
                }
            )
        elif str(num) == str(13):
            instance = str(problemManagerChannel.id) + "___" + str(session_id)
            # Who does this go to?
            # Or do we just log here?
            '''
            async_to_sync(get_channel_layer().group_send)(
                instance,
                {
                    'type': 'chat.message',
                    'message': Interventions.NO_INTERVENTION,
                    'sender': "Process Manager",
                    'channel': instance
                }
            )
            '''
