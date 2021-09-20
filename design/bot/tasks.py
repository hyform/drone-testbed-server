from celery import Celery
from celery import shared_task
from celery.utils.log import get_task_logger
from exper.models import UserPosition, Session, User
from design.celery import app
from django.conf import settings
#import websocket
import threading
import time

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(type(error))
    print(repr(error))

def on_close(ws, close_status_code, close_msg):
    print(close_status_code)
    print(close_msg)
    print("### closed ###")

def on_open(ws):
    print("hello open")
    def run(*args):
        for i in range(3):
            time.sleep(1)
            ws.send("Hello %d" % i)
        time.sleep(1)
        ws.close()
        print("thread terminating...")
    threading.Thread(target=run).start()

# Task to start a bot
@app.task
def bot_connect(session_id, position_id):
    # Make websocket connection to local server
    websocket_host = settings.LOCAL_ADDRESS
    websocket_origin = settings.LOCAL_ORIGIN
    websocket_port = settings.LOCAL_PORT
    websocket_proto = "ws"
    if settings.LOCAL_SSL:
        websocket_proto = "wss"

    bot_key = settings.BOT_SECRET_KEY

    # TODO: may end up with different consumers for different roles
    websocket_url = websocket_proto + '://' + websocket_host + ':' + websocket_port + '/ws/bot/' \
        + '?s_id=' + str(session_id) \
        + '&p_id=' + str(position_id) \
        + '&bot_key=' + bot_key

    ws = websocket.WebSocketApp(websocket_url,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    wst = threading.Thread(target=ws.run_forever)
    #wst.daemon = True
    wst.start()
