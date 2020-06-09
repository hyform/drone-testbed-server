# This is an example of callinn into the UAVDesginer and getting a response

import grpc

from . import uavdesign_pb2_grpc as uavdesign_pb2_grpc
from . import uavdesign_pb2 as uavdesign_pb2

def design_assess(stub):
    design = uavdesign_pb2.UAVDesign(config = "*aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3")
    results = stub.GetUAVPerformance(design)
    print("The result is %s" % results.result)
    print("range: %s, velocity %s, cost %s" %(results.range, results.velocity, results.cost))

def run():
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = uavdesign_pb2_grpc.DesignAssessStub(channel)
        design_assess(stub)

if __name__ == '__main__':
    run()
