# You'll need to
# pip install websocket-client
# in your local python env to run this

import requests
import json
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time

r = requests.post('http://localhost:8081/api-token-auth/', data = {'username':'hyform-exper', 'password':'experpassword'})
token = r.json()['token']
print(token)

def on_open(ws):
	def run(*args):
		ws.send(json.dumps({
			'type' : 'twin.start',      # this is where initial team inputs will go
            'unit_structure' : 1,       # for now, just use 1
            'market' : 1,               # for now, just use 1
            'ai' : 1,                   # for now, just use 1
			'channel' : 'twin'
		}))

	thread.start_new_thread(run, ())

def on_message(ws, message):
    message_dict = json.loads(message)
    type = message_dict['type']
    if type == 'twin.info':
        info = message_dict['info']
        print("info : " + str(info))
    elif type == 'twin.complete':
        info = message_dict['info']
        print("close : " + str(info))
        ws.close()


ws = websocket.WebSocketApp("ws://localhost:8081/ws/chat/?token=" + token,
	on_open = on_open,
	on_message = on_message)

ws.run_forever()
