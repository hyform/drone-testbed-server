from celery import Celery
import numpy as np
from celery import shared_task, signature
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings

import subprocess, select

import grpc

from . import uavdesign_pb2_grpc as uavdesign_pb2_grpc
from . import uavdesign_pb2 as uavdesign_pb2

from repo.views import MediationCountView, MediationChatView
from process.messaging import send_intervention
from exper.models import Session
from chat.models import Channel
from api.models import SessionTimer
from ai.agents.botmanager import BotManager

import time

mediation_means = {
    'semantics': [-0.006743317, 0.075710224, 0.252834778, 0.320476221, 0.434859771, 0.369622907, 0.374351602, 0.442302754, 0.57186047, 0.539848064, 0.542159886, 0.364853707],
    'parameter':[0.909090909, 5.909090909, 12.72727273, 16.90909091, 17.27272727, 18.09090909, 9.181818182, 24.45454545, 31.09090909, 28.90909091, 27.18181818, 23.18181818],
    'strategy': [0.272727273, 1.181818182, 2.454545455, 4.454545455, 6, 5.545454545, 2.545454545, 6.545454545, 7.545454545, 6.818181818, 6.818181818, 6.272727273],
    'comms_ops': [1.545454545, 5.818181818, 9.272727273, 10.63636364, 12, 11.18181818, 5.636363636, 12.72727273, 13.54545455, 14.72727273, 15, 12.09090909],
    'comms_design': [0.363636364, 2.181818182, 3.181818182, 3.454545455, 4.090909091, 4.454545455, 3.090909091, 6.181818182, 6.454545455, 6.454545455, 6.090909091, 6.272727273],
    'comms_pm': [0, 0.818181818, 1.454545455, 1.454545455, 1.909090909, 2.181818182, 2, 4.636363636, 5.545454545, 5.727272727, 4.363636364 ,3.363636364],
    'act_ops_iter': [44.09090909, 123.1818182, 163.0909091, 165.9090909, 178.2727273, 215.8181818, 90.54545455, 225.9090909, 250.7272727, 212.0909091, 201.1818182, 232.9090909],
    'act_ops_submit': [0, 0.272727273, 0.727272727, 0.909090909, 1.727272727, 3.363636364, 0.636363636, 1.363636364, 2.636363636, 2.818181818, 2, 1.818181818],
    'act_ops_AI': [0.454545455, 1.636363636, 2.727272727, 2.454545455, 2.818181818, 3.727272727, 2.181818182, 4.727272727, 5.272727273, 4.272727273, 4.272727273, 7],
    'act_design_iter': [10.72727273, 50.81818182, 89.72727273, 95.18181818, 79.18181818, 74.81818182, 36.81818182, 79.18181818, 89.54545455, 92.45454545, 84.45454545, 77.09090909],
    'act_design_submit': [3.272727273, 12.27272727, 20.18181818, 23.27272727, 23.54545455, 21.27272727, 5.363636364, 17.54545455, 23.54545455, 24.27272727, 23.09090909, 22.54545455],
    'act_design_AI': [0.636363636, 2.090909091, 3.181818182, 3.363636364, 3.454545455, 3.818181818, 1.454545455, 2.727272727, 3.363636364, 3.727272727, 3, 3.181818182],
    'comms_overall': [1.909090909, 8.818181818, 13.90909091, 15.54545455, 18, 17.81818182, 10.72727273, 23.54545455, 25.54545455, 26.90909091, 25.45454545, 21.72727273],
    'act_overall': [44.45454545, 126.1818182, 167.7272727, 170.8181818, 184.2727273, 222.4545455, 95.63636364, 236.7272727, 262.7272727, 224.2727273, 211.6363636, 242.5454545]
}

mediation_ranges = {
    'semantics': [0.006743317, 0.07637271, 0.101968027, 0.063874788, 0.061561722, 0.100042811, 0.056865293, 0.052962256, 0.044693506, 0.054305009, 0.045959809, 0.090285048],
    'parameter': [0.392070157, 1.681203819, 2.697105887, 2.598791836, 3.116206637, 3.966804405, 1.672331969, 3.28734111, 3.553371115, 3.00440448, 4.414476561, 4.57824536],
    'strategy': [0.140835758, 0.325246251, 0.679085433, 0.856670472, 1.095445115, 1.073343429, 0.856670472, 1.147040749, 1.090151252, 0.829218491, 1.622669976, 1.595965989],
    'comms_ops': [0.561874078, 1.488245959, 1.768876937, 1.613988438, 2.686667419, 2.448814859, 1.32303183, 2.110970949, 1.983402203, 1.972957674, 2.351015255, 2.454882132],
    'comms_design': [0.203278907, 0.806994219, 1.034128371, 0.975738754, 1.115629015, 0.927985466, 0.653028545, 1.204674093, 1.274673836, 1.691495499, 1.642916174, 1.446569039],
    'comms_pm': [0.01, 0.422507274, 0.528525158, 0.365902033, 0.624565965, 0.644108712, 0.53935989, 0.834186891, 0.824220142, 0.714663418, 0.591957113, 0.591957113],
    'act_ops_iter': [4.438375103, 16.20595748, 25.19359751, 20.523359, 21.89067502, 27.97622958, 14.29962723, 27.67192688, 26.59907412, 27.66535561, 29.17870275, 41.54044131],
    'act_ops_submit': [0.01, 0.194978278, 0.359062139, 0.250619068, 0.428335236, 0.677867341, 0.278721995, 0.337712284, 0.472377493, 0.501238136, 0.687551651, 0.615233611],
    'act_ops_AI': [0.247299464, 0.876695524, 1.526081787, 1.302889351, 1.007410558, 1.722001526, 0.932427739, 2.071849894, 2.280713242, 1.902586321, 1.732527891, 3.238967288],
    'act_design_iter': [4.47232075, 13.49600492, 19.83022987, 21.4297237, 13.88643431, 15.53519066, 11.16473196, 16.25916144, 17.80008357, 22.29201391, 21.63850257, 17.513867],
    'act_design_submit': [0.428335236, 2.565827561, 3.79908645, 3.466963327, 4.077351271, 3.729710954, 1.574066692, 3.656534963, 2.98591736, 2.873360114, 3.576322503, 4.095149318],
    'act_design_AI': [0.309625207, 0.609836721, 0.902704843, 0.834186891, 0.994198045, 0.784140315, 0.454545455, 0.810060706, 0.741898391, 1.045256898, 1.206045378, 1.256388633],
    'comms_overall': [0.680301343, 2.219001339, 2.465966694, 1.922893825, 3.539388751, 3.541489624, 1.819544944, 3.122829825, 2.563249487, 2.209296661, 2.718166616, 3.000275469],
    'act_overall': [4.394963308, 15.62155747, 24.83402758, 20.69774611, 21.55841574, 27.60578452, 14.09724198, 27.16183516, 26.80606814, 28.61248644, 29.74750493, 41.83829556]
}

mediation_effects = {
    'size': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    'action': [1.80288777, 2.17290127, 2.850687951, 2.606531812, 0.989601334, 0.533969019, 0.111649015, 0.061209231, 0.499725346, 2.028169488, 4.105751966, 2.652089303],
    'communication': [0.021762202, 0.099391388, 1.036494627, 2.620418475, 3.791209304, 2.447290812, 0.572214632, 0.75524772, 4.094955577, 2.841478881, 1.746172813, 0.768509383]
}

# app = Celery('design')
channel_layer = get_channel_layer()
logger = get_task_logger(__name__)

# @app.task
@shared_task
def sum(channel_name, data):
    logger.info('in sum task')
    data['result'] = data.get('x', 0) + data.get('y',0)
    async_to_sync(channel_layer.send)(channel_name, {"type": "task.return","results": data})

@shared_task
def assess_design(channel_name, data):
    logger.info('in assess_design task')
    config = data.get('config', '*aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3')
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = uavdesign_pb2_grpc.DesignAssessStub(channel)
        logger.info('got a channel to the evaluation')
        design = uavdesign_pb2.UAVDesign(config = config)
        logger.info('submitted config: %s', config)
        results = stub.GetUAVPerformance(design)
        logger.info('got results from evaluation')
        data['result'] = results.result
        data['range'] = results.range
        data['velocity'] = results.velocity
        data['cost'] = results.cost
    async_to_sync(channel_layer.send)(channel_name, {"type": "task.return","results": data})

@shared_task
def eval_design(channel_name, data):
    logger.info('in eval_design task')
    config = '-configuration "' + data.get('config', '*aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3')+'"'
    logger.info(config)
    parts = config.split(',')
    if len(parts) > 1:
        tmp_payload = parts[1]
        try:
            payload = float(tmp_payload)
        except ValueError:
            pass

    process=subprocess.Popen([settings.EVALUATION_APP, '-batchmode', '-nographics', config],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    logger.info('created subprocess')
    try:
        out, err = process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        logger.info('had to kill eval')
        process.kill()
        out, err = process.communicate()
        logger.info(out)
        logger.info(err)

    logger.info('got eval results')
    logger.info(out)
    tokens = out.splitlines()[-1].split()
    logger.info(out.splitlines()[-1])
    for t in tokens:
        logger.info(t)
    data['result'] = "Success"
    data['range'] = float(tokens[1])
    data['cost'] = float(tokens[3])
    data['velocity'] = float(tokens[2])
    data['payload'] = payload
    logger.info('results: %s', data['result'])
    async_to_sync(channel_layer.send)(channel_name, {"type": "task.return","results": data})

@shared_task
def evaluation(config, trajectory):

    if not config:
        return {}
    payload = 0
    parts = config.split(',')
    if len(parts) > 1:
        tmp_payload = parts[1]
        try:
            payload = float(tmp_payload)
        except ValueError:
            pass
    args = []
    args.append(settings.EVALUATION_APP)
    args.append('-batchmode')
    args.append('-nographics')
    if trajectory:
        args.append('-trajectory')
    args.append('-configuration')
    args.append(config)

    process=subprocess.Popen(
        args,
        bufsize=8192,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    out = bytearray()
    err = bytearray()
    done = False

    start_time = time.time()

    while ((process.returncode is None) or (not done)) and (time.time() - start_time < 10):

        process.poll()
        done = False

        ready = select.select([process.stdout, process.stderr], [], [], 1.0)

        if process.stderr in ready[0]:
            data = process.stderr.read(1024)
            if len(data) > 0:
                err = err + data

        if process.stdout in ready[0]:
            #data = process.stdout.read(1024)
            data = process.stdout.readline()
            if len(data) == 0:
                done = True
            else:
                out = out + data

    lines = out.splitlines()
    num_lines = len(lines)
    current_line = 0

    while current_line < num_lines:
        #print("input: " + str(lines[current_line]))
        current_line_str = bytes(lines[current_line]).decode('UTF-8')
        if current_line_str == "RESULTS":
            break
        current_line = current_line + 1

    current_line = current_line + 1

    out_data = {}
    if current_line < num_lines:
        #print("input: " + str(lines[current_line]))
        results = lines[current_line].split()
        evaluation_data = {}
        evaluation_data['result'] = bytes(results[0]).decode('UTF-8')
        evaluation_data['range'] = float(results[1])
        evaluation_data['cost'] = float(results[3])
        evaluation_data['velocity'] = float(results[2])
        evaluation_data['payload'] = float(payload)
        out_data["evaluation"] = evaluation_data

        trajectory_data = []
        current_line = current_line + 1
        while current_line < num_lines:
            traj_values = lines[current_line].split()
            traj_data = {}
            traj_data['time'] = float(traj_values[0])
            traj_data['pos_x'] = float(traj_values[1])
            traj_data['pos_y'] = float(traj_values[2])
            traj_data['pos_z'] = float(traj_values[3])
            traj_data['rx'] = float(traj_values[4])
            traj_data['ry'] = float(traj_values[5])
            traj_data['rz'] = float(traj_values[6])
            traj_data['rw'] = float(traj_values[7])
            trajectory_data.append(traj_data)
            current_line = current_line + 1
        out_data["trajectory"] = trajectory_data

    # return out_data

    return out_data

@shared_task
def mediation(seg_num, seg_len, i, session_id, timestamp):
    # This routine will call itself many times to determine the correct mediation to send out
    # get the current session
    session = Session.objects.get(id=session_id)
    running_timer = SessionTimer.objects.filter(session=session).filter(timer_type=SessionTimer.RUNNING_START).first()
    if session.status != Session.RUNNING or timestamp != str(running_timer.timestamp):
        print("Session restarted or no longer running, so exit mediation loop")
        return

    print(i, session.name, session.index)
    if i < seg_num:
        # first step is to schedule the next time to call
        mediation.s(seg_num, seg_len, i+1, session_id, timestamp).apply_async(countdown=seg_len)
        # we don't care about the first 2 times (time 0 and time 2.5 minutes)
        if i<2:
            print('waiting for next interval')
        else:
            index = 6*(session.index-1)+i-2
            index = 6*(session.index-1)+i-2
            # view = MediationCountView()
            count_data = MediationCountView().get_data(session_id=session_id, section_id=i-2)
            total_comms = count_data['comms_ops'] + count_data['comms_design'] + count_data['comms_pm']
            total_act = count_data['act_ops_iter'] + count_data['act_ops_submit'] + count_data['act_ops_AI']
            total_act += count_data['act_design_iter'] + count_data['act_design_submit'] + count_data['act_design_AI']
            z_score_comms = (total_comms - mediation_means['comms_overall'][index])/mediation_ranges['comms_overall'][index]
            z_score_act = (total_act - mediation_means['act_overall'][index])/mediation_ranges['act_overall'][index]
            print(index, z_score_comms, z_score_act)

            intervention_id = 13

            # lets calculate action z_scores
            action_scores=np.zeros(6)
            action_scores[0] = (count_data['act_ops_iter']-mediation_means['act_ops_iter'][index])/mediation_ranges['act_ops_iter'][index]
            action_scores[1] = (count_data['act_ops_submit']-mediation_means['act_ops_submit'][index])/mediation_ranges['act_ops_submit'][index]
            action_scores[2] = (count_data['act_ops_AI']-mediation_means['act_ops_AI'][index])/mediation_ranges['act_ops_AI'][index]
            action_scores[3] = (count_data['act_design_iter']-mediation_means['act_design_iter'][index])/mediation_ranges['act_design_iter'][index]
            action_scores[4] = (count_data['act_design_submit']-mediation_means['act_design_submit'][index])/mediation_ranges['act_design_submit'][index]
            action_scores[5] = (count_data['act_design_AI']-mediation_means['act_design_AI'][index])/mediation_ranges['act_design_AI'][index]
            action_id = np.argmin(action_scores) + 1
            print(action_scores)
            print('action score id: ', action_id)
            if z_score_comms>-1:
                 # first case to test is no internvetion
                if z_score_act >-1:
                    intervention_id=13
                else:
                    # enter action branch
                    intervention_id = action_id

            else:
                chat_data = MediationChatView().get_data(session_id=session_id, section_id=i-2)
                # calculate comms z scores
                comm_scores=np.zeros(6)
                comm_scores[0] = (chat_data['parameter']-mediation_means['parameter'][index])/mediation_ranges['parameter'][index]
                comm_scores[1] = (chat_data['strategy']-mediation_means['strategy'][index])/mediation_ranges['strategy'][index]
                comm_scores[2] = (chat_data['semantics']-mediation_means['semantics'][index])/mediation_ranges['semantics'][index]
                comm_scores[3] = (count_data['comms_ops']-mediation_means['comms_ops'][index])/mediation_ranges['comms_ops'][index]
                comm_scores[4] = (count_data['comms_design']-mediation_means['comms_design'][index])/mediation_ranges['comms_design'][index]
                comm_scores[5] = (count_data['comms_pm']-mediation_means['comms_pm'][index])/mediation_ranges['comms_pm'][index]
                comm_id = np.argmin(comm_scores) + 7
                print('comm score id: ', comm_id)

                if z_score_act > -1:
                    # enter comms branch
                    intervention_id = comm_id
                else:
                    # which is the most "bad"
                    com = np.abs(z_score_comms * mediation_effects['communication'][index])
                    act = np.abs(z_score_act * mediation_effects['action'][index])
                    if com>act:
                        #enter comm branch
                        intervention_id = comm_id
                    else:
                        #enter act branch
                        intervention_id = action_id
            # this is a test message to the designer

            print("final intervention send: ", intervention_id)
            send_intervention(None, intervention_id, session_id)

    else:
        print('done looping')
        end_running.delay(session_id, timestamp)
    return i

@shared_task
def end_running(session_id, timestamp):
    session = Session.objects.filter(id=session_id).first()
    running_timer = SessionTimer.objects.filter(session=session).filter(timer_type=SessionTimer.RUNNING_START).first()
    if session:
        if session.status == Session.RUNNING and timestamp == str(running_timer.timestamp):
            session.status = Session.POSTSESSION
            session.save()
            session_channel = Channel.objects.filter(name="Session").first()
            session_instance = str(session_channel.id) + "___" + str(session.id)

            async_to_sync(get_channel_layer().group_send)(
                session_instance,
                {
                    'type': 'system.command',
                    'message': "refresh",
                    'sender': "System",
                    'channel': session_instance
                }
            )

            exercise = session.exercise
            if exercise:
                experiment = exercise.experiment
                if experiment:
                    study = experiment.study
                    if study:
                        organization = study.organization
                        if organization:
                            help_channel = Channel.objects.filter(name="Help").first()
                            channel_instance = str(help_channel.id) + "_organization_" + str(organization.id)
                            async_to_sync(get_channel_layer().group_send)(
                                channel_instance,
                                {
                                    'type': 'system.command',
                                    'message': "experimenter-reload",
                                    'sender': "System",
                                    'channel': channel_instance
                                }
                            )

#@shared_task
def bot_timer(seg_num, seg_len, i, session_id, timestamp):
    print("bot_timer get session")
    # This routine will call itself many times to determine the correct mediation to send out
    # get the current session
    session = Session.objects.get(id=session_id)
    print("got session")
    running_timer = SessionTimer.objects.filter(session=session).filter(timer_type=SessionTimer.RUNNING_START).first()
    if session.status != Session.RUNNING or timestamp != str(running_timer.timestamp):
        print("Session restarted or no longer running, so exit bot loop")
        return

    if i < seg_num:
        # first step is to schedule the next time to call
        bot_timer.s(seg_num, seg_len, i+1, session_id, timestamp).apply_async(countdown=seg_len)
        # we don't care about the first 2 times (time 0 and time 2.5 minutes)
        if i == 0 or i == 1 or i == 2:
            BotManager.register_timed_event(session_id, "iterate")
    return i


@shared_task
def mediation_loop(data):
    seg_num = settings.INTER_SEG_NUM
    seg_len = settings.INTER_SEG_LEN

    # this routine will start up the mediation cycle
    running_timer = SessionTimer.objects.filter(session__id=data['session_id']).filter(timer_type=SessionTimer.RUNNING_START).first()
    mediation.s(seg_num, seg_len, 0, data['session_id'], str(running_timer.timestamp)).apply_async()

@shared_task
def human_mediation_loop(data):
    seg_num = settings.INTER_SEG_NUM
    seg_len = settings.INTER_SEG_LEN
    total_len = seg_num * seg_len

    # Only need to schedule the end for human process manager
    running_timer = SessionTimer.objects.filter(session__id=data['session_id']).filter(timer_type=SessionTimer.RUNNING_START).first()
    end_running.s(data['session_id'], str(running_timer.timestamp)).apply_async(countdown=total_len)

@shared_task
def bot_loop(data):

    seg_num = settings.INTER_SEG_NUM
    seg_len = settings.INTER_SEG_LEN

    # this routine will start up the mediation cycle
    running_timer = SessionTimer.objects.filter(session__id=data['session_id']).filter(timer_type=SessionTimer.RUNNING_START).first()
    bot_timer.s(seg_num, seg_len, 0, data['session_id'], str(running_timer.timestamp)).apply_async()
