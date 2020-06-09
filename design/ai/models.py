from django.db import models
import grpc
from . import uavdesign_pb2_grpc as uavdesign_pb2_grpc
from . import uavdesign_pb2 as uavdesign_pb2

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

import math
import sys

import xml.etree.ElementTree as ET
from xml.dom import minidom

# Create your models here.

class Designer1(models.Model):
    config = models.CharField(max_length=500)
    range = models.FloatField()
    cost = models.FloatField()
    payload = models.FloatField()

class UAVDesign(object):
    def __init__(self, config):
        self.config = config
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = uavdesign_pb2_grpc.DesignAssessStub(channel)
            self.design_assess(stub)
        self.result = self.results.result
        self.range = self.results.range
        self.velocity = self.results.velocity
        self.cost = self.results.cost

    def design_assess(self, stub):
        # replace the hardcode string with self.config
        # design = uavdesign_pb2.UAVDesign(config = "*aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3")
        design = uavdesign_pb2.UAVDesign(config = self.config)
        self.results = stub.GetUAVPerformance(design)

class UAVDesign2(object):
    def __init__(self, config):
        self.config = config
        with grpc.insecure_channel('localhost:50052') as channel:
            stub = uavdesign_pb2_grpc.DesignAssessStub(channel)
            self.design_assess(stub)
        self.result = self.results.result
        self.range = self.results.range
        self.velocity = self.results.velocity
        self.cost = self.results.cost

    def design_assess(self, stub):
        # replace the hardcode string with self.config
        # design = uavdesign_pb2.UAVDesign(config = "*aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3")
        design = uavdesign_pb2.UAVDesign(config = self.config)
        self.results = stub.GetUAVPerformance(design)

class UAVDesignTraj2(object):
    def __init__(self, config):
        self.config = config
        with grpc.insecure_channel('localhost:50052') as channel:
            stub = uavdesign_pb2_grpc.DesignAssessStub(channel)
            self.design_assess(stub)
        results = self.trajresult.results
        self.trajs = self.trajresult.trajs
        self.result = results.result
        self.range = results.range
        self.velocity = results.velocity
        self.cost = results.cost
        # need to add the trajectory stuff yet - just calling the stub for it now

    def design_assess(self, stub):
        # replace the hardcode string with self.config
        # design = uavdesign_pb2.UAVDesign(config = "*aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3")
        design = uavdesign_pb2.UAVDesign(config = self.config)
        self.trajresult = stub.GetUAVTrajectory(design)


class OpsPlan1(object):
    def __init__(self, input):
        self.input = input
        #self.output = self.input
        self.output = self.runLP(self.input)


    def create_data_model( self, sc, inputdemands, inputdemandstype, num_vehicles, vehicle_range, vehicle_velocity, vehicle_payload_capacity, positions):
        """Stores the data for the problem."""
        data = {}

        data['inputdemands'] = inputdemands
        data['inputdemandstype'] = inputdemandstype
        data['num_vehicles'] = num_vehicles

        data['vehicle_capacities'] = []
        for i in range(data['num_vehicles']):
            data['vehicle_capacities'].append(vehicle_payload_capacity)

        data['vehicle_ranges'] = []


        for i in range(data['num_vehicles']):
            data['vehicle_ranges'].append(int(sc*vehicle_range/vehicle_velocity))



        data['vehicle_velocity'] = vehicle_velocity
        data['positions'] = positions
        data['distance_matrix'] = []
        for i in range(len(data['positions'])):
            dist_row = []
            for j in range(len(data['positions'])):
                dist_row.append(math.sqrt(math.pow(data['positions'][i][0] - data['positions'][j][0], 2) + math.pow(data['positions'][i][1] - data['positions'][j][1], 2)))
            data['distance_matrix'].append(dist_row)

        data['package_demands'] = []
        data['food_demands'] = []
        data['time_windows'] = []
        for i in range(len(data['inputdemandstype'])):
            if data['inputdemandstype'][i] == "package":
                data['package_demands'].append(data['inputdemands'][i])
                data['food_demands'].append(0)
                data['time_windows'].append((0,sc*24))
            else:
                data['package_demands'].append(0)
                data['food_demands'].append(data['inputdemands'][i])
                if data['inputdemandstype'][i] == "food1":
                    data['time_windows'].append((0,sc*2))
                else:
                    data['time_windows'].append((sc*4,sc*6))

        data['time_matrix'] = [row[:] for row in data['distance_matrix']]
        for i in range(len(data['time_matrix'])):
            for j in range(len(data['time_matrix'])):
                data['time_matrix'][i][j] = int(sc*data['distance_matrix'][i][j]/data['vehicle_velocity'])

        data['depot'] = 0

        return data

    def intersection(self, lst1, lst2):
        lst3 = [value for value in lst1 if value in lst2]
        return lst3


    def start(self, originalinputdemands, inputdemands, inputdemandstype, num_vehicles, vehicle_range, vehicle_velocity, vehicle_payload_capacity, positions):

        sc = 1000

        """Solve the VRP with time windows."""
        data = self.create_data_model(sc, inputdemands, inputdemandstype, num_vehicles, vehicle_range, vehicle_velocity, vehicle_payload_capacity, positions)
        manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
                                               data['num_vehicles'], data['depot'])
        routing = pywrapcp.RoutingModel(manager)

        def time_callback(from_index, to_index):
            """Returns the travel time between the two nodes."""
            # Convert from routing variable Index to time matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['time_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(time_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        time = 'Time'
        routing.AddDimension(
            transit_callback_index,
            sc*30,  # allow waiting time
            sc*30,  # maximum time per vehicle
            False,  # Don't force start cumul to zero.
            time)
        time_dimension = routing.GetDimensionOrDie(time)

        dimension_name = 'Distance'
        routing.AddDimensionWithVehicleCapacity(
            transit_callback_index,
            0,  # no slack
            data['vehicle_ranges'],  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name)
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(1)

        # Add Capacity constraint.
        def demand_callback(from_index):
            """Returns the demand of the node."""
            # Convert from routing variable Index to demands NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return data['package_demands'][from_node] + data['food_demands'][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data['vehicle_capacities'],  # vehicle maximum capacities
            True,  # start cumul to zero
            'Capacity')

        # Allow to drop nodes.
        penalty = 100000000

        for node in range(1, len(data['time_matrix'])):
            dd = 1
            try:
                if data['inputdemandstype'][node] == "food2":
                    dd = 4
            except Exception as e:
                pass
            routing.AddDisjunction([manager.NodeToIndex(node)], dd*penalty)


        # Add time window constraints for each location except depot.
        for location_idx, time_window in enumerate(data['time_windows']):
            if location_idx == 0:
                continue
            index = manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        # Add time window constraints for each vehicle start node.
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            time_dimension.CumulVar(index).SetRange(data['time_windows'][0][0],
                                                    data['time_windows'][0][1])
        for i in range(data['num_vehicles']):
            routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(routing.Start(i)))
            routing.AddVariableMinimizedByFinalizer(
                time_dimension.CumulVar(routing.End(i)))
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        #search_parameters.first_solution_strategy = (
        #    routing_enums_pb2.FirstSolutionStrategy.LOCAL_CHEAPEST_INSERTION)
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)



        assignment = routing.SolveWithParameters(search_parameters)

        remaining_locations = []
        for node in range(routing.Size()):
            if routing.IsStart(node) or routing.IsEnd(node):
                continue
            if assignment.Value(routing.NextVar(node)) == node:
                remaining_locations.append(manager.IndexToNode(node))

        time_dimension = routing.GetDimensionOrDie('Time')
        total_time = 0
        paths = []
        pathTimes = []
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
            path = []
            pathTimes = []
            pathTime = 0
            while not routing.IsEnd(index):
                path.append(manager.IndexToNode(index))
                time_var = time_dimension.CumulVar(index)
                plan_output += '{0} Time({1},{2}) -> '.format(
                    manager.IndexToNode(index), assignment.Min(time_var),
                    assignment.Max(time_var))
                index = assignment.Value(routing.NextVar(index))
                pathTime = 1.0*assignment.Min(time_var)/sc
                pathTimes.append(pathTime)
            time_var = time_dimension.CumulVar(index)
            plan_output += '{0} Time({1},{2})\n'.format(manager.IndexToNode(index),
                                                        assignment.Min(time_var),
                                                        assignment.Max(time_var))
            plan_output += 'Time of the route: {}min\n'.format(
                assignment.Min(time_var))
            total_time += assignment.Min(time_var)

            total_payload = 0;
            for i in range(len(path)):
                total_payload += originalinputdemands[path[i]]

            paths.append([path, assignment.Min(time_var)/sc, total_payload, pathTimes])


        return [remaining_locations, paths, total_time/sc]

    def runLP(self, s):
        mydoc = minidom.parseString(s)
        lppositions = mydoc.getElementsByTagName('Position')
        basePosition = mydoc.getElementsByTagName('BasePosition')
        lpvehicles = mydoc.getElementsByTagName('Vehicle')

        inputdemands = []
        inputdemandstype = []
        vehicles = []  # number , range, velocity, payloadCap
        positions = []

        positions.append([float(basePosition[0].attributes["x"].value), float(basePosition[0].attributes["z"].value)])
        inputdemands.append(0)
        inputdemandstype.append("package")

        # set positions
        for i in range(len(lppositions)):
            if lppositions[i].attributes["selected"].value == "True":
                positions.append([float(lppositions[i].attributes["x"].value), float(lppositions[i].attributes["z"].value)])
                inputdemands.append(int(lppositions[i].attributes["payload"].value))
                inputdemandstype.append(lppositions[i].attributes["type"].value)
            else:
                positions.append([float(lppositions[i].attributes["x"].value), float(lppositions[i].attributes["z"].value)])
                inputdemands.append(0)
                inputdemandstype.append(lppositions[i].attributes["type"].value)

        for i in range(len(lpvehicles)):
            vehicles.append([int(lpvehicles[i].attributes["quantity"].value), float(lpvehicles[i].attributes["range"].value), float(lpvehicles[i].attributes["velocity"].value), float(lpvehicles[i].attributes["payload"].value)])

        unsatisfied = []
        for i in range(1, len(inputdemands)):
            if inputdemands[i] > 0:
                unsatisfied.append(i)

        # make this better
        vehiclePaths = []
        vehiclePathTimes = []

        total_time = 0
        total_mass = 0

        total_package = 0
        total_food1 = 0
        total_food2 = 0

        no_satisfied = 0

        max_time = 0
        for i in range(len(vehicles)):
            step_input_demands = []
            for j in range(len(inputdemands)):
                step_input_demands.append(10000)
            for j in range(len(unsatisfied)):
                step_input_demands[unsatisfied[j]] = inputdemands[unsatisfied[j]]
            step_input_demands[0] = 0

            results = self.start(inputdemands, step_input_demands, inputdemandstype, vehicles[i][0], vehicles[i][1], vehicles[i][2], vehicles[i][3], positions)
            pathdata = results[1]
            for i in range(len(pathdata)):
                pathdatarow = pathdata[i]
                travel_path = pathdatarow[0]
                travel_path_times = pathdatarow[3]
                vehiclePathTimes.append(travel_path_times)
                vehiclePath = {}
                vehiclePath['vehicle_index'] = i
                vehiclePath['path'] = pathdatarow[0]
                vehiclePath['path_travel_time'] = pathdatarow[1]
                vehiclePath['mass_delivered'] = pathdatarow[2]
                vehiclePaths.append(vehiclePath)
                total_mass += pathdatarow[2]
                total_time += pathdatarow[1]
                max_time = max(max_time, pathdatarow[1])
                path_package = 0
                path_food1 = 0
                path_food2 = 0
                for j in range(len(travel_path)):
                    if travel_path[j] != 0:
                        no_satisfied += 1
                    if inputdemandstype[travel_path[j]] == "package":
                        total_package += inputdemands[travel_path[j]]
                        path_package += inputdemands[travel_path[j]]
                    elif inputdemandstype[travel_path[j]] == "food1":
                        total_food1 += inputdemands[travel_path[j]]
                        path_food1 += inputdemands[travel_path[j]]
                    elif inputdemandstype[travel_path[j]] == "food2":
                        total_food2 += inputdemands[travel_path[j]]
                        path_food2 += inputdemands[travel_path[j]]
                vehiclePath['package_delivered'] = path_package
                vehiclePath['food1_delivered'] = path_food1
                vehiclePath['food2_delivered'] = path_food2

            unsatisfied = self.intersection(unsatisfied, results[0])

        data = ET.Element('results')

        item1 = ET.SubElement(data, 'total_customers_satisfied')
        item1.text = str(no_satisfied)

        item2 = ET.SubElement(data, 'total_mass_delivered')
        item2.text = str(total_mass)

        vehicle_travel_item = ET.SubElement(data, 'total_vehicle_travel_time')
        vehicle_travel_item.text = str(total_time)

        max_path_duration_item = ET.SubElement(data, 'max_path_duration')
        max_path_duration_item.text = str(max_time)

        total_mass_item = ET.SubElement(data, 'total_mass')
        total_mass_item.text = str(total_mass)

        total_mass_package_delivered_item = ET.SubElement(data, 'total_mass_package_delivered')
        total_mass_package_delivered_item.text = str(total_package)

        total_mass_food1_delivered_item = ET.SubElement(data, 'total_mass_food1_delivered')
        total_mass_food1_delivered_item.text = str(total_food1)

        total_mass_food2_delivered_item = ET.SubElement(data, 'total_mass_food2_delivered')
        total_mass_food2_delivered_item.text = str(total_food2)

        item3 = ET.SubElement(data, 'paths')
        for i in range(len(vehiclePaths)):
            pathitem = ET.SubElement(item3, 'path')
            p = vehiclePaths[i]["path"]
            for j in range(len(p)):
                pathpositemitem = ET.SubElement(pathitem, 'p')
                pathpositemitem.text = str(p[j])
                pathpositemitem.set("delivered_time", str((vehiclePathTimes[i][j])))

        # add path times to the results


        # create a new XML file with the results
        rough_string = ET.tostring(data, 'utf-8').decode("utf-8")

        return rough_string
