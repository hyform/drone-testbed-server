from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

import math
import json
import sys


def create_data_model(sc, inputdemands, inputdemandstype, num_vehicles,
                      vehicle_range, vehicle_velocity, vehicle_payload_capacity, positions):
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
            dist_row.append(math.sqrt(math.pow(data['positions'][i][0] - data['positions'][j][0], 2) + math.pow(
                data['positions'][i][1] - data['positions'][j][1], 2)))
        data['distance_matrix'].append(dist_row)

    data['package_demands'] = []
    data['food_demands'] = []
    data['time_windows'] = []
    for i in range(len(data['inputdemandstype'])):
        if data['inputdemandstype'][i] == "package":
            data['package_demands'].append(data['inputdemands'][i])
            data['food_demands'].append(0)
            data['time_windows'].append((0, sc*24))
        else:
            data['package_demands'].append(0)
            data['food_demands'].append(data['inputdemands'][i])
            data['time_windows'].append((sc*4, sc*6))

    data['time_matrix'] = [row[:] for row in data['distance_matrix']]
    for i in range(len(data['time_matrix'])):
        for j in range(len(data['time_matrix'])):
            data['time_matrix'][i][j] = int(
                sc*data['distance_matrix'][i][j]/data['vehicle_velocity'])

    data['depot'] = 0

    return data


def start(originalinputdemands, inputdemands, inputdemandstype, num_vehicles,
          vehicle_range, vehicle_velocity, vehicle_payload_capacity, positions):

    sc = 1000

    """Solve the VRP with time windows."""
    data = create_data_model(sc, inputdemands, inputdemandstype, num_vehicles,
                             vehicle_range, vehicle_velocity, vehicle_payload_capacity, positions)
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

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Allow to drop nodes.
    penalty = 100000000

    # dropout penalty, try to fulfill food , can adjust this in the future
    for node in range(1, len(data['time_matrix'])):
        dd = 1
        try:
            if data['inputdemandstype'][node] == "food2":
                dd = 4
        except Exception as e:
            print(e)
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
    # search_parameters.first_solution_strategy = (
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

        total_payload = 0
        for i in range(len(path)):
            total_payload += originalinputdemands[path[i]]

        paths.append(path)

    return [remaining_locations, paths, total_time/sc]


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


if __name__ == '__main__':

    # will send a string of this format
    ########## accepts a Plan json object with empty paths, each path has a vehicle with metrics  ##########
    file_object = open("plan.json", 'r')
    plan_json = json.load(file_object)

    # list to store OR tools
    inputdemands = []
    inputdemandstype = []
    vehicles = []  # number , range, velocity, payloadCap
    positions = []

    # add warehouse to first position
    positions.append([float(plan_json['scenario']['warehouse']['address']['x']), float(
        plan_json['scenario']['warehouse']['address']['z'])])
    inputdemands.append(0)
    inputdemandstype.append("package")

    # add locations and demands based on scenario
    for customer in plan_json['scenario']['customers']:
        positions.append([float(customer['address']['x']),
                          float(customer['address']['z'])])
        inputdemandstype.append(customer['payload'])
        if customer['selected']:
            inputdemands.append(int(customer['weight']))
        else:
            inputdemands.append(0)

    # add vehicles based on the plan paths, where each path has a vehicle
    for vehicle_path in plan_json['paths']:
        vehicles.append([1,                                   # quantity
                         float(vehicle_path['vehicle']
                               ['range']),        # range
                         float(vehicle_path['vehicle']
                               ['velocity']),     # velocity
                         float(vehicle_path['vehicle']['payload'])])     # payload

    # add this list to identify what locations are not delivered to
    unsatisfied = []
    for i in range(1, len(inputdemands)):
        if inputdemands[i] > 0:
            unsatisfied.append(i)

    vehiclePaths = []

    # independent vehicle analysis
    # was a multiple capacity routing problem based on distance until they wanted time windows
    # with vehicles of differnet velocities, that changed the underlying time time_matrix for each vehicle
    # so each vehicle is run indedenedntly of the others
    for i in range(len(vehicles)):

        # set demand to high if already satisfied by a previous vehicle
        step_input_demands = []
        for j in range(len(inputdemands)):
            step_input_demands.append(10000)
        for j in range(len(unsatisfied)):
            step_input_demands[unsatisfied[j]] = inputdemands[unsatisfied[j]]
        step_input_demands[0] = 0  # warehouse

        # run path finding for the vehicle, vehicles[i][0-3] quantity, range, velocity, payload
        results = start(inputdemands, step_input_demands, inputdemandstype,
                        vehicles[i][0], vehicles[i][1], vehicles[i][2], vehicles[i][3], positions)

        # parse the results from the or tools anaylsis
        pathdata = results[1]
        for i in range(len(pathdata)):
            travel_path = pathdata[i]
            vehiclePaths.append(travel_path)
            print(travel_path)

        # unsatisfied nodes
        unsatisfied = intersection(unsatisfied, results[0])

    # append scenario customers to the plan path
    for i in range(len(vehiclePaths)):
        p = vehiclePaths[i]
        for j in range(len(p)):
            if(int(p[j]) != 0):  # not warehouse
                plan_json['paths'][i]['customers'].append(plan_json['scenario']['customers'][int(
                    p[j]) - 1])  # index - 1 since the warehouse is in the first position

    ########## return the plan json object with customers appended to the path ##########
    with open("plan_with_customers.json", 'w') as outfile:
        json.dump(plan_json, outfile)
