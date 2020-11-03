from celery import Celery
import numpy as np
from celery import shared_task
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings

import subprocess, select

import grpc

from . import uavdesign_pb2_grpc as uavdesign_pb2_grpc
from . import uavdesign_pb2 as uavdesign_pb2

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
    #logger.info('in eval_design task')
    config = '-config "' + data.get('config', '*aMM0++++++++++++++*bNM2+++*cMN1+++*dLM2+++*eML1+++*fOM3*gMO3*hKM3*iMK3*jPM2+++*kMP1+++*lJM2+++*mMJ1+++^ab^ac^ad^ae^bf^cg^dh^ei^fj^gk^hl^im,50,3')+'"'
    #logger.info(config)
    process=subprocess.Popen([settings.EVALUATION_APP, '-batchmode', '-nographics', config],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    #logger.info('created subprocess')
    try:
        out, err = process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        logger.info('had to kill eval')
        process.kill()
        out, err = process.communicate()
        logger.info(out)
        logger.info(err)

    #logger.info('got eval results')
    tokens = out.splitlines()[-1].split()
    data['result'] = "Success"
    data['range'] = float(tokens[0])
    data['cost'] = float(tokens[2])
    data['velocity'] = float(tokens[1])
    #logger.info('results: %s', data['result'])
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
    while (process.returncode is None) or (not done):
        process.poll()
        done = False

        ready = select.select([process.stdout, process.stderr], [], [], 1.0)

        if process.stderr in ready[0]:
            data = process.stderr.read(1024)
            if len(data) > 0:
                err = err + data

        if process.stdout in ready[0]:
            data = process.stdout.read(1024)
            if len(data) == 0:
                done = True
            else:
                out = out + data

    lines = out.splitlines()
    num_lines = len(lines)
    current_line = 0
        
    while current_line < num_lines:
        print("input: " + str(lines[current_line]))
        current_line_str = bytes(lines[current_line]).decode('UTF-8')
        if current_line_str == "RESULTS":
            break
        current_line = current_line + 1

    current_line = current_line + 1

    out_data = {}
    if current_line < num_lines:
        print("input: " + str(lines[current_line]))
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

    return out_data