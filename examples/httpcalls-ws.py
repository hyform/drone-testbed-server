import requests
import json
import websocket
import traceback
try:
    import thread
except ImportError:
    import _thread as thread
import time

r = requests.post('http://localhost:8081/api-token-auth/', data = {'username':'hyform-exper', 'password':'experpassword'})
token = r.json()['token']
print(token)


my_counter = 0

def on_open(ws):
    def run(*args):
        create_session()
    thread.start_new_thread(run, ())

def on_message(ws, message):

    try:

        global my_counter

        message_dict = json.loads(message)
        type = message_dict['type']
        if type == 'twin.info':

            info = str(message_dict['info'])
            session_id = str(message_dict['session_id'])

            print(str(session_id) + " info : " + info + " ")

            if 'session_created_id' in info:

                # send preference, set uncertainty, or run analysis
                send_preference(session_id)
                #send_uncertainty(session_id)
                #run_session(session_id)

            # if desired, set the pause interval in the run session command ( the first run session command detrermines the pause interval throughout the simulation)
            # session will stay paused until a run command is sent
            # here is where you would do something
            # buffer for about 5 seconds
            if 'session_paused' in info:
                my_counter += 1
                if my_counter > 5:
                    run_session(session_id)
                    my_counter = 0

        # check if received a preference save
        if type == 'twin.pref':
            info = message_dict['info']
            session_id = str(message_dict['session_id'])
            if 'preference_set' in str(info):
                # run session of send uncertainty
                send_uncertainty(session_id)
                #run_session(session_id)

        if type == 'twin.uncertainty':
            info = message_dict['info']
            session_id = str(message_dict['session_id'])
            if 'uncertainty_set' in str(info):
                # run session or set preference
                run_session(session_id)
                # send_preference(session_id)

        if type == 'twin.log':
            print("log : uncomment next line in code to view the full log")    # uncomment the next line to see full log
            #print("log : " + str(message_dict["time"])[:4] + " : " + message_dict["usr"] + " : " + message_dict["action"])
        if type == 'twin.complete':
            print("completed")
            ws.close()

    except Exception as e:
        with open("error.txt", "a") as myfile:
            myfile.write(traceback.format_exc())
        myfile.close()


def create_session():
	ws.send(json.dumps({
		'type' : 'twin.start',      # this is where initial team inputs will go
        'unit_structure' : 1,       # for now, just use 1
        'market' : 1,               # for now, just use 1
        'ai' : 1,                   # for now, just use 1, since the analysis currently does not prevent using AI agents
		'channel' : 'twin'
	}))

def run_session(session_id):
    ws.send(json.dumps({
        'type' : 'twin.run',
        'session_id' : session_id,
        'pause_interval' : 20,      # interval for pauses in minutes, set to 20 or higher for no pauses
        'channel' : 'twin'
    }))

def send_preference(session_id):

    NOPREFERENCE = 0

    prefs = {'channel' : 'twin',
        'type' : 'twin.pref',
        'session_id' : session_id,
        'prefs' : [                     # the below result in close approaximation to planners and designers to historical trends, with underperforming a bit in the final selected business plan
            {

                'user_id' : 'arl_1',
                'pref_type' : 1,        # 0 weight sums, 1 target or goal based, for now use 0
                'profit' : 9000,
                'cost' : 15000,
                'no_customers' : 36
            },
            {
                'user_id' : 'arl_2',
                'pref_type' : 1,        # 0 weight sums, 1 target or goal based, for now use 0
                'range' : NOPREFERENCE,
                'capacity' : NOPREFERENCE,
                'cost' : NOPREFERENCE
            },
            {
                'user_id' : 'arl_3',
                'pref_type' : 1,        # 0 weight sums, 1 target or goal based, for now use 0
                'range' : NOPREFERENCE,
                'capacity' : NOPREFERENCE,
                'cost' : NOPREFERENCE
            },
            {
                'user_id' : 'arl_4',
                'pref_type' : 1,        # 0 weight sums, 1 target or goal based, for now use 0
                'profit' : 9000,
                'cost' : 15000,
                'no_customers' : 36
            },
            {
                'user_id' : 'arl_5',
            },
            {
                'user_id' : 'arl_6'
            }
        ],
        'reqs' : [
            {
                'user_id' : 'arl_1',
                'profit': {
                    'min' : 1000,
                    'max' : 1000000
                },
                'cost': {
                    'min' : 0,
                    'max' : 15000
                },
                'no_customers': {
                    'min' : 0,
                    'max' : 1000000
                }
            },
            {
                'user_id' : 'arl_2',
                'range': {
                    'min' : 10,
                    'max' : 20
                },
                'capacity': {
                    'min' : 10000,
                    'max' : 15000
                },
                'cost': {
                    'min' : 0,
                    'max' : 30
                },
                'no_structures': {
                    'min' : 2,
                    'max' : 4
                }
            },
            {
                'user_id' : 'arl_4',
                'profit': {
                    'min' : 1000,
                    'max' : 1000000
                },
                'cost': {
                    'min' : 0,
                    'max' : 15000
                },
                'no_customers': {
                    'min' : 0,
                    'max' : 1000000
                }
            }

        ]

    }

    ws.send(json.dumps(prefs))

ws = websocket.WebSocketApp("ws://localhost:8081/ws/chat/?token=" + token,
	on_open = on_open,
	on_message = on_message)

def send_uncertainty(session_id):

    uncertainties = {'channel' : 'twin',
        'type' : 'twin.uncertainty',
        'session_id' : session_id,
        'uncertainties' : [                     # deviation by location, where a locations demand is adjusted by its delivery weight +- random[-deviation, deviation]
            {
                'x' : -0.8,
                'z' : 6.4,
                'deviation' : 1.0
            },
            {
                'x' : -0.7,
                'z' : 7.2,
                'deviation' : 0.6
            },
        ]
    }

    ws.send(json.dumps(uncertainties))

ws = websocket.WebSocketApp("ws://localhost:8081/ws/chat/?token=" + token,
	on_open = on_open,
	on_message = on_message)

ws.run_forever()