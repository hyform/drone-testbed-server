from celery import Celery
import numpy as np
from celery import shared_task
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import subprocess

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
    logger.info('in eval_design task')

