import argparse
import os
import pandas as pd
import random
import numpy
import math
import json
import traceback

from ai.models import OpsService
from repo.models import Scenario, Vehicle, Plan, Customer, Path, PathCustomer, Warehouse, CustomerScenario
from chat.messaging import new_plan_message
from ai.models import OpsPlan

from .database_helper import DatabaseHelper
from repo.serializers import PlanSerializer
#from .generate_role_sequences import GenerateRoleSequences

from api.messaging import twin_info_message, twin_complete_message


# initializes a team of agents based on an experimental session and then starts a team simulation in a new thread
class AdaptiveTeamAIUpdatedPlanner():

    def __init__(self, session, digital_twin_setups):

        self.session = session
        self.db_helper = DatabaseHelper(session)

        self.designer_sequences = pd.read_csv(r'static/ai/ai_designer_sequences_updated.txt', sep='\t')
        self.planner_sequences = pd.read_csv(r'static/ai/ai_planner_sequences_updated.txt', sep='\t')
        self.business_sequences = pd.read_csv(r'static/ai/ai_business_sequences.txt', sep='\t')

        self.real_time = False

        self.team_role = {}
        self.team_data = {}
        self.team_time_events = {}

        self.plan_cache = {}

        self.business_scenario_submitted = False
        self.business_select_event = None
        self.business_selected = False

        # initialize team
        user_roles = self.db_helper.get_user_roles()
        for usr in user_roles:
            # for now, assign N events for each usr and times based on October 2020 experimental data
            # may need to make this more adaptive
            if 'Business' in user_roles[usr]:
                self.team_role[usr] = "business"
                self.team_data[usr] = None
                # since business is 'one' process, will just use the sampled RNN string to simulate all events
                # designer and planner have Opens, which kind of 'restart' the user with new sequences
            elif 'Design' in user_roles[usr]:
                number_of_designer_events_dist = [0.56, 0.625, 0.75, 1.0, 0.5, 0.437, 0.25, 0.125, 0.0625, 0.0625]
                number_of_designer_events = self.sample_from_binned_dist(number_of_designer_events_dist, 4, 75)
                designer_time_events= self.linear_trend(0.28, 0.72, 0, 20, number_of_designer_events)
                designer_time_events.sort()
                self.team_role[usr] = "designer"
                self.team_data[usr] = None
                self.team_time_events[usr] = designer_time_events
            elif 'Plan' in user_roles[usr]:
                number_of_planner_events_dist = [0.42, 0.31, 0.17, 0.07, 0.0, 0.01, 0, 0, 0, 0.01]
                number_of_planner_events = int(self.sample_from_binned_dist(number_of_planner_events_dist, 1, 180))
                planner_time_events= self.linear_trend(0.32, 0.68, 0, 20, number_of_planner_events)
                planner_time_events.sort()
                self.team_role[usr] = "planner"
                self.team_data[usr] = None
                self.team_time_events[usr] = planner_time_events

        # code to presample and generate role event sequences
        #g = GenerateRoleSequences()

        # setup simulation
        self.actions_queue = []
        self.current_time = -1
        current_action_index = 0

        # sample initial events
        self.generate_initial_events()

        # run simulation
        while current_action_index < len(self.actions_queue):
            self.run_action(self.actions_queue[current_action_index])
            current_action_index += 1


        # clean up operations
        # if business did not select a final plan
        if not self.business_selected:

            # set database user
            business_usr = None
            for usr in self.team_role:
                if self.team_role[usr] == 'business':
                    self.db_helper.set_user_name(usr)
                    business_usr = usr

            # in the rare case with no submitted plan, submit any plans from planners
            plans = self.db_helper.query_plans()
            if len(plans) == 0:
                for usr in user_roles:
                    if self.team_role[usr] == "planner" and self.team_data[usr] is not None:
                        self.run_action([20, usr, [0, "Submit", 0]])

            # select a final plan
            counter = 0 # to prevent infinite loop
            while not self.business_selected and counter < 100:
                if self.business_select_event is not None:
                    self.business_select_event[0] = 20
                    self.run_action(self.business_select_event)
                    self.business_select_event = None
                else: # randomly select a business sequence with a Select event
                    idx = random.randrange(0, 605)
                    events = self.business_sequences.query("seq == " + str(idx)).values.tolist()
                    for event in events:
                        if 'Selected' in event[1]:
                            self.run_action([20, business_usr, event])
                counter += 1

    # runs a design, planner, or business action in the simulation
    def run_action(self, action):

        try:

            print("action",action)
            twin_info_message("action")
            twin_info_message(action)

            # probably need to develop a event object, instead of using lists
            t = action[0]
            usr = action[1]
            self.current_time = t
            self.db_helper.set_user_name(usr)

            # if business event
            if self.team_role[usr] == "business":
                action_info = action[2][1].split(";")

                # for now, restricting to one scenario submit , that is the reason for the second condition
                if action_info[0] == "Scenario" and not self.business_scenario_submitted:

                    # locations to include in the scenario
                    # format of the AI is inverse to the agent code, so a bunch of string modifications
                    locations = action_info[1].replace("|",";").replace(":", "|").split(";")

                    # gets the current scenario
                    scenario = self.db_helper.get_scenario()
                    no_matching_scenario_locations = []

                    select_nodes = {}
                    number_selected = 0

                    # initially , unselect all customers
                    for customer in scenario['customers']:
                        key_test = str(customer['address']['x']) + "|" + str(customer['address']['z'])
                        select_nodes[key_test] = 'False'

                    # find and set customers if the locations match
                    for customer in scenario['customers']:
                        key_test = str(customer['address']['x']) + "|" + str(customer['address']['z'])
                        if key_test in locations:
                            select_nodes[key_test] = 'True'
                            number_selected += 1
                            locations.remove(key_test)

                    # if no match, find the closest customer (maybe to support new markets or shocks)
                    for remaining_loc in locations:
                        closestKey = None
                        closestDistance = 10000000000000
                        if len(remaining_loc.split("|")) > 1:
                            x = float(remaining_loc.split("|")[0])
                            z = float(remaining_loc.split("|")[1])
                            for customer in scenario['customers']:
                                key_test = str(customer['address']['x']) + "|" + str(customer['address']['z'])
                                d = (float(customer['address']['x']) - x)**2 + (float(customer['address']['z']) - z)**2
                                if d < closestDistance:
                                    closestKey = key_test
                                    closestDistance = d

                        if closestKey is not None:
                            select_nodes[closestKey] = 'True'
                            number_selected += 1

                    # submit the scenario
                    scenario_str = self.db_helper.submit_scenario(select_nodes)
                    # add datalog event
                    self.db_helper.submit_data_log(usr, "SubmitScenario;" + scenario_str, self.real_time, t)
                    self.resample_planners_based_on_scenario_and_vehicles()
                    self.write_business_metrics(t, usr, "Scenario", number_selected, 0, 0, scenario_str)
                    self.business_scenario_submitted = True

                # open plan , gets all current available team plans and selects a plan with the close metrics
                if action_info[0] == "Open":
                    close_plan = self.get_close_plan(float(action_info[1]),float(action_info[2]),float(action_info[3]), False)
                    if close_plan is not None:
                        json_plan = self.convert_plan_json(close_plan)
                        self.team_data[usr] = json_plan
                        plan_str = self.convert_plan_json_to_str(json_plan)
                        result = OpsService(plan_str)
                        metricstr = "Profit," + str(result.profit) + ",OperatingCost," + str(result.operating_cost) + ",StartUpCost," + str(result.startupCost) + ",Number of Deliveries," + str(result.number_deliveries) + ",MassDelivered," + str(result.total_weight_delivered) + ",Parcel," + str(result.total_parcel_delivered) + ",Food," + str(result.total_food_delivered)
                        # add datalog event
                        self.db_helper.submit_data_log(usr, "Opened;" + json_plan['tag'] + ";" + plan_str + ";" + metricstr, self.real_time, t)
                        self.write_business_metrics(t, usr, "Open", result.profit, result.startupCost, result.number_deliveries, "")

                if action_info[0] == "Selected" and t >= 18:
                    #closest_plan = self.get_closest_plan(float(action_info[1]), float(action_info[2]), float(action_info[3]), True)
                    # since the business in underperforming compared to historical data, add a far reaching goal
                    closest_plan = self.get_close_plan(7000, float(action_info[2]), 40, True)
                    #closest_plan = self.get_closest_plan(float(action_info[1]), float(action_info[2]), float(action_info[3]), True)
                    if closest_plan is not None and not self.business_selected:
                        closest_plan_json = self.convert_plan_json(closest_plan)
                        self.business_selected = True
                        plan_str = self.convert_plan_json_to_str(closest_plan_json)         # create a string representation of the plan
                        result = OpsService(plan_str)
                        metricstr = "Profit," + str(result.profit) + ",OperatingCost," + str(result.operating_cost) + ",StartUpCost," + str(result.startupCost) + ",Number of Deliveries," + str(result.number_deliveries) + ",MassDelivered," + str(result.total_weight_delivered) + ",Parcel," + str(result.total_parcel_delivered) + ",Food," + str(result.total_food_delivered)
                        # add datalog event
                        self.db_helper.submit_data_log(usr, "BusinessPlanSelected;" + closest_plan_json['tag'] + ";" + str(closest_plan_json['id']) + ";" + plan_str + ";" + metricstr, self.real_time, t)
                        self.write_business_metrics(t, usr, "Selected", result.profit, result.startupCost, result.number_deliveries, "")
                        print("-------------------------------- Business Selected --------------------------------", metricstr)
                        twin_info_message("-------------------------------- Business Selected --------------------------------")
                        twin_info_message(metricstr)

                # save selected event for at the end of the session
                if action_info[0] == "Selected" and t < 18 and self.business_select_event is None:
                    self.business_select_event = action

            # if a designer event
            if self.team_role[usr] == "designer":
                if action[2][2] == "Submit" and self.is_design_unique(usr, action[2][1]):
                    tag = "design:" + usr + ":" + str(t)
                    self.db_helper.submit_vehicle_db(tag, action[2][1], action[2][3], action[2][4], action[2][5], action[2][6])
                    # add datalog event
                    self.db_helper.submit_data_log(usr, "SubmitToDB;" + tag + ";range=" + str(action[2][3]) + ",capacity=" + str(action[2][4]) + ",cost=" + str(action[2][5]) + ",velocity=" + str(action[2][6]), self.real_time, t)
                    self.resample_planners_based_on_scenario_and_vehicles()
                    self.write_designer_metrics(t, usr, "Submit", action[2][3], action[2][4], action[2][5], action[2][1])
                elif action[2][2] == "Open":
                    selected_vehicle_data = self.resample_designer_based_on_metrics(usr, action[2][3], action[2][4], action[2][5], False)
                    # add datalog event
                    self.db_helper.submit_data_log(usr, "Open;tag=" + selected_vehicle_data[0] + ";config=" + selected_vehicle_data[1] + ";range=" + str(selected_vehicle_data[2]) + ",capacity=" + str(selected_vehicle_data[3]) + ",cost=" + str(selected_vehicle_data[4]) + ",velocity=" + str(selected_vehicle_data[5]), self.real_time, t)
                    self.write_designer_metrics(t, usr, "Open", selected_vehicle_data[2], selected_vehicle_data[3], selected_vehicle_data[4], selected_vehicle_data[1])
                else:   # evaluate
                    # add datalog event
                    self.db_helper.submit_data_log(usr, "Evalauted;" + action[2][2] + ";range=" + str(action[2][3]) + ",capacity=" + str(action[2][4]) + ",cost=" + str(action[2][5]) + ",velocity=" + str(action[2][6]), self.real_time, t)
                    self.write_designer_metrics(t, usr, "Evaluated", action[2][3], action[2][4], action[2][5], action[2][1])

            # if planner event, saving plans in json format, since using model object appears to need to be saved to the central database
            if self.team_role[usr] == "planner":

                action_str = action[2][1]
                tokens = action_str.split("_")

                # represents the start of a session
                if "Start" in tokens[0]:

                    # reset plan
                    plan = {}
                    plan['paths'] = []
                    plan['tag'] = usr + ":" + str(t)
                    plan['scenario'] = self.db_helper.get_scenario()
                    self.team_data[usr] = plan

                # submits a plan if there is one stored
                if "Submit" in tokens[0] and self.team_data[usr] is not None:

                    # get plan for a user
                    plan = self.team_data[usr]
                    if plan is not None:
                        plan_str = self.convert_plan_json_to_str(self.team_data[usr])
                        result = OpsService(plan_str)
                        metrics = "Profit," + str(result.profit) + ",OperatingCost," + str(result.operating_cost) + ",StartUpCost," + str(result.startupCost) + ",Number of Deliveries," + str(result.number_deliveries) + ",MassDelivered," + str(result.total_weight_delivered) + ",Parcel," + str(result.total_parcel_delivered) + ",Food," + str(result.total_food_delivered)

                        # if profit
                        if result.profit > 0 and self.is_plan_unique(usr, result.profit, result.startupCost, result.number_deliveries):
                            self.db_helper.plan_submit(plan)
                            # add datalog event
                            self.db_helper.submit_data_log(usr, "SubmitPlanToDB;" + plan['tag'] + ";" + plan_str + ";" + metrics, self.real_time, self.current_time)
                            self.write_planner_metrics(self.current_time, usr, "Submit", result.profit, result.startupCost, result.number_deliveries)
                            print("---- Submit Plan ---- ", metrics)
                            twin_info_message("---- Submit Plan ---- ")
                            twin_info_message(metrics)
                        else:
                            print("plan had zero profit : not submitting")
                            twin_info_message("plan had zero profit : not submitting")

                # opens the closest plan
                if "Open" in tokens[0]:

                    # get metrics of the Open event
                    metrics = tokens[0].split("=")[1].split(",")
                    profit = float(metrics[0])
                    startupCost = float(metrics[1])
                    no_deliveries = float(metrics[2])

                    # get a close plan
                    close_plan = self.get_close_plan(profit, startupCost, no_deliveries, False)
                    if close_plan is not None:
                        close_plan_json = self.convert_plan_json(close_plan)
                        self.team_data[usr] = close_plan_json
                        plan_str = self.convert_plan_json_to_str(close_plan_json)
                        result = OpsService(plan_str)
                        metrics = "Profit," + str(result.profit) + ",OperatingCost," + str(result.operating_cost) + ",StartUpCost," + str(result.startupCost) + ",Number of Deliveries," + str(result.number_deliveries) + ",MassDelivered," + str(result.total_weight_delivered) + ",Parcel," + str(result.total_parcel_delivered) + ",Food," + str(result.total_food_delivered)
                        # add datalog event
                        self.db_helper.submit_data_log(usr, "Opened;" + close_plan_json['tag'] + ";" + plan_str + ";" + metrics, self.real_time, t)
                        self.write_planner_metrics(t, usr, "Open", result.profit, result.startupCost, result.number_deliveries)

                # runs the planner AI agent
                elif "Agent" in tokens[0]:

                    metrics = tokens[0].split("=")[1]

                    # create the plan input string with empty paths, where each path has a closest vehicle as recommended by the planner AI
                    plan = {}
                    paths = []
                    scenario_obj = self.db_helper.get_scenario()

                    deliveries = tokens[1].split("Path")
                    for delivery in deliveries:
                        if len(delivery) > 0:

                            try:
                                path_metrics = delivery.split(";")
                                vehicle_str = path_metrics[0]
                                vehiclerange = int(vehicle_str.split("c")[0][1:])
                                vehiclecapacity = int(vehicle_str.split("c")[1].split("$")[0])
                                vehiclecost = int(vehicle_str.split("c")[1].split("$")[1])
                                used_vehicle = self.get_closest_vehicles([[vehiclerange, vehiclecapacity, vehiclecost]])[0]

                                path_obj = {}
                                vehicle_obj = {}
                                vehicle_obj['id'] = used_vehicle.id
                                vehicle_obj['tag'] = used_vehicle.tag
                                vehicle_obj['config'] = used_vehicle.config
                                vehicle_obj['range'] = used_vehicle.range
                                vehicle_obj['cost'] = used_vehicle.cost
                                vehicle_obj['payload'] = used_vehicle.payload
                                vehicle_obj['velocity'] = used_vehicle.velocity
                                path_obj['vehicle'] = vehicle_obj
                                path_obj['customers'] = []
                                path_obj['warehouse'] = scenario_obj['warehouse']
                                paths.append(path_obj)
                            except Exception as e:
                                print(e)
                                twin_info_message(e)

                    plan['paths'] = paths
                    plan['scenario'] = scenario_obj

                    json_str = json.dumps(plan)

                    # use planner agent to create new plan
                    o = OpsPlan(json_str)
                    plan_ai_json = o.output.replace("\'","\"").replace("True", "true").replace("False", "false")

                    # save the plan json object
                    json_obj_plan = json.loads(plan_ai_json)

                    # set tag
                    json_obj_plan['tag'] = "ai_" + usr + ":" + str(t)

                    # save the plan to the user
                    self.team_data[usr] = json_obj_plan

                    # convert the json plan to a string to save to a dataLog and calculate metrics
                    plan_str = self.convert_plan_json_to_str(json_obj_plan)

                    # get the metrics of the new plan
                    result = OpsService(plan_str)
                    metrics = "Profit," + str(result.profit) + ",OperatingCost," + str(result.operating_cost) + ",StartUpCost," + str(result.startupCost) + ",Number of Deliveries," + str(result.number_deliveries) + ",MassDelivered," + str(result.total_weight_delivered) + ",Parcel," + str(result.total_parcel_delivered) + ",Food," + str(result.total_food_delivered)
                    # add datalog event
                    self.db_helper.submit_data_log(usr, "PathAgentResult;" + plan_str + ";" + metrics, self.real_time, t)
                    self.write_planner_metrics(t, usr, "PathAgent", result.profit, result.startupCost, result.number_deliveries)

                # user manually builds a path
                elif "Manual" in tokens[0] and self.team_data[usr] is not None:

                    # reset plan, since the manual event includes all path information
                    # for all vehicles in the plan
                    plan = {}
                    plan['paths'] = []
                    plan['tag'] = usr + ":" + str(t)
                    scenario_obj = self.db_helper.get_scenario()
                    plan['scenario'] = scenario_obj
                    self.team_data[usr] = plan

                    # get path tokens
                    add_path_tokens = tokens[1].split(";")
                    current_path = None
                    added_to_plan = False
                    for path_token in add_path_tokens:
                        # vehicle tokens have $ in the token
                        if "$" in path_token: # vehicle

                            # get the vehicle metrics from the token
                            results = self.get_vehicle_metrics(path_token)
                            # get closest vehicle in the session
                            used_vehicle = self.get_closest_vehicles([[results[0], results[1], results[2]]])[0]

                            # create and add an empty vehicle path and set as the current path
                            path_obj = {}
                            vehicle_obj = {}
                            vehicle_obj['id'] = used_vehicle.id
                            vehicle_obj['tag'] = used_vehicle.tag
                            vehicle_obj['config'] = used_vehicle.config
                            vehicle_obj['range'] = used_vehicle.range
                            vehicle_obj['cost'] = used_vehicle.cost
                            vehicle_obj['payload'] = used_vehicle.payload
                            vehicle_obj['velocity'] = used_vehicle.velocity
                            path_obj['vehicle'] = vehicle_obj
                            path_obj['customers'] = []
                            path_obj['warehouse'] = scenario_obj['warehouse']
                            self.team_data[usr]["paths"].append(path_obj)
                            current_path = path_obj

                        # if there is a current path and the token is a location
                        elif current_path is not None and len(path_token.split(",")) > 1:

                            customer_str_x = float(path_token.split(",")[0])
                            customer_str_z = float(path_token.split(",")[1])

                            # get closest unselected feasible customer
                            closest_customer = None
                            clostest_distance = 100000000

                            # copy path
                            cp_path = []
                            for customer in current_path['customers']:
                                cp_path.append(customer)

                            # for each customer, get its proximity to the suggestion and if it is feasible and not already included
                            for customer in scenario_obj['customers']:

                                if customer['selected']:

                                    customer_x = float(customer['address']['x'])
                                    customer_z = float(customer['address']['z'])

                                    append_cp_path = []
                                    already_in_path = False
                                    for customer_copy in cp_path:
                                        append_cp_path.append(customer_copy)
                                        if float(customer_copy['address']['x']) == customer_x and float(customer_copy['address']['z']) == customer_z:
                                            already_in_path = True

                                    if not already_in_path:

                                        # append customer to path
                                        append_cp_path.append(customer)

                                        # get distance from customer based on suggested location
                                        d = ((customer_str_x - customer_x)**2 + (customer_str_z - customer_z)**2)*0.5

                                        # get distance of path to see if it is feasible
                                        last_customer = None
                                        current_range = 0
                                        current_capacity = 0
                                        for ii, customer_cp in enumerate(append_cp_path):
                                            # get distance from warehouse to first customer , or from the previous customer
                                            if ii == 0:
                                                current_range += ((float(customer_cp['address']['x']) - float(scenario_obj['warehouse']['address']['x']))**2 + (float(customer_cp['address']['z']) - float(scenario_obj['warehouse']['address']['z']))**2)**0.5
                                            else:
                                                current_range += ((float(customer_cp['address']['x']) - float(last_customer['address']['x']))**2 + (float(customer_cp['address']['z']) - float(last_customer['address']['z']))**2)**0.5
                                            current_capacity += customer['weight']
                                            last_customer = customer

                                        # add return path to warehouse
                                        current_range += ((float(last_customer['address']['x']) - float(scenario_obj['warehouse']['address']['x']))**2 + (float(last_customer['address']['z']) - float(scenario_obj['warehouse']['address']['z']))**2)**0.5

                                        # check if the total range and capacity of the path is supported by the path vehicle
                                        if current_range <= current_path['vehicle']['range'] and current_capacity <= current_path['vehicle']['payload']:
                                            if d < clostest_distance:
                                                closest_customer = customer
                                                clostest_distance = d

                            # for this location token, add a selected customer
                            if closest_customer is not None:
                                current_path['customers'].append(closest_customer)
                                added_to_plan = True

                    # add log data
                    if added_to_plan:
                        # convert the json plan to a string to save to a DataLog and calculate metrics
                        plan_str = self.convert_plan_json_to_str(self.team_data[usr])
                        result = OpsService(plan_str)
                        metrics = "Profit," + str(result.profit) + ",OperatingCost," + str(result.operating_cost) + ",StartUpCost," + str(result.startupCost) + ",Number of Deliveries," + str(result.number_deliveries) + ",MassDelivered," + str(result.total_weight_delivered) + ",Parcel," + str(result.total_parcel_delivered) + ",Food," + str(result.total_food_delivered)
                        # add datalog event
                        self.db_helper.submit_data_log(usr, "ManualPathOperation;" + ";" + plan_str + ";" + metrics, self.real_time, t)
                        self.write_planner_metrics(t, usr, "ManualPathOperation", result.profit, result.startupCost, result.number_deliveries)


        except Exception as e:
            print("---- RNN parser error ----")
            twin_info_message("---- RNN parser error ----")
            traceback.print_exc()
            pass

    def is_design_unique(self, usr, config):
        vehicles = self.db_helper.query_vehicles()
        for v in vehicles:
            if v.config == config:
                return False
        return True

    def is_plan_unique(self, usr, profit, startupCost, number_deliveries):
        plans = self.db_helper.query_plans()
        for p in self.plan_cache:
            metrics = self.plan_cache[p]
            if metrics[0] == profit and metrics[1] == startupCost and metrics[2] == number_deliveries:
                return False
        return True

    def generate_initial_events(self):
        for usr in self.team_role:
            if self.team_role[usr] == "designer":
                self.resample_designer_based_on_metrics(usr, 10, 5, 3470, True)
            elif self.team_role[usr] == "planner":
                self.resample_planner_based_on_scenario_and_vehicles(usr)
            elif self.team_role[usr] == "business":
                self.sample_business_events(usr)

    # resample the designer user to try and find a sequence to the closest team design as generated by the RNN sequence
    def resample_designer_based_on_metrics(self, usr, range, capacity, cost, start_sequence):

        all_events = []

        self.db_helper.set_user_name(usr)
        # starting seqeunce and new session (just base vehicle)
        vehicles = self.db_helper.query_vehicles()
        if start_sequence and len(vehicles) == 1:
            starting_events = self.designer_sequences.query("type == 'Submit' and start_submit == 1").values.tolist()
            idx = random.randrange(0, len(starting_events))
            seq_events = []
            # get sequences of some length
            while len(seq_events) < 4:
                seq_events = self.designer_sequences.query("seq == " + str(starting_events[idx][0])).values.tolist()
                idx = random.randrange(0, len(starting_events))

            for event in seq_events:
                all_events.append(event)
                range = event[3]
                capacity = event[4]
                cost = event[5]

        # sample new events
        # random sampling, this is where one can add mediation sampling
        first_event_data = self.sample_design_sequence_starting_open_design(range, capacity, cost)

        # get last design
        last_range = first_event_data[7]
        last_capacity = first_event_data[8]
        last_cost = first_event_data[9]

        first_events = first_event_data[0]
        #first_events.pop(0)
        for event in first_events:
            all_events.append(event)
        while len(all_events) < len(self.team_time_events[usr]):
            event_data = self.sample_design_sequence_starting_open_design(last_range, last_capacity, last_cost)
            last_range = event_data[7]
            last_capacity = event_data[8]
            last_cost = event_data[9]

            events = event_data[0]

            for event in events:
                all_events.append(event)

        self.assign_events_to_user(usr, all_events)

        return [first_event_data[1], first_event_data[2], first_event_data[3],first_event_data[4],first_event_data[5],first_event_data[6]  ]

    def resample_planners_based_on_scenario_and_vehicles(self):
        for usr in self.team_role:
            if self.team_role[usr] == "planner":
                self.resample_planner_based_on_scenario_and_vehicles(usr)

    def resample_planner_based_on_scenario_and_vehicles(self, usr):

        self.db_helper.set_user_name(usr)
        vehicles = self.db_helper.query_vehicles()
        scenario = self.db_helper.get_scenario()

        locations = []
        for customer in scenario['customers']:
            locations.append(str(customer['address']['x']) + "," + str(customer['address']['z']))

        current_vehicles = []
        for vehicle in vehicles:
            # bias away from base vehicle
            if len(vehicles) == 1:
                current_vehicles.append([vehicle.range, vehicle.payload, vehicle.cost])
            elif vehicle.tag != "base":
                current_vehicles.append([vehicle.range, vehicle.payload, vehicle.cost])

        # set upper limits for vehicles
        max_range = 100
        max_capacity = 99
        max_cost = 15000

        loc_seqs = {}
        veh_seqs = {}
        path_len = {}   # add bias to find longer paths
        path_feasbility = {}
        max_path_len = 0
        show_error = True
        for planner_event in self.planner_sequences.values.tolist():
            try:

                event_path_length = 0
                plan_cost = 0

                location_tokens = planner_event[1].split(";")
                seq_id = planner_event[0]
                if seq_id not in loc_seqs:
                    loc_seqs[seq_id] = [0, 0]
                if seq_id not in veh_seqs:
                    veh_seqs[seq_id] = [0, 0]
                if seq_id not in path_len:
                    path_len[seq_id] = []
                if seq_id not in path_feasbility:
                    path_feasbility[seq_id] = []
                if len(location_tokens) > 1:
                    for i in range(len(location_tokens)):
                        # look for location tokens , with three tokens split using , x , z, weight
                        location_tokens_test = location_tokens[i].split(",")
                        if (len(location_tokens_test) == 2 or len(location_tokens_test) == 3) and "$" not in location_tokens_test:
                            try:
                                x = location_tokens_test[0]
                                z = location_tokens_test[1]
                                loc_token = x + "," + z
                                if loc_token in locations:
                                    loc_seqs[planner_event[0]] = [loc_seqs[seq_id][0] + 1, loc_seqs[seq_id][1]]
                                loc_seqs[planner_event[0]] = [loc_seqs[seq_id][0], loc_seqs[seq_id][1] + 1]
                                event_path_length += 1
                                if event_path_length > max_path_len:
                                    max_path_len = event_path_length
                            except Exception as f:
                                print(f)
                                twin_info_message(f)
                        if "$" in location_tokens[i]:
                            token_test = location_tokens[i].replace("Manual","")
                            if "Path" in token_test:
                                token_test = token_test.split("Path")[1]
                            token_test = token_test.replace("_","")
                            metrics = self.get_vehicle_metrics(token_test)

                            plan_cost += metrics[2]

                            # get closest
                            min_d = 10000000
                            for veh in current_vehicles:
                                veh_d = (((veh[0] - metrics[0])/max_range)**2 + ((veh[1] - metrics[1])/max_capacity)**2 + ((veh[2] - metrics[2])/max_cost)**2)**0.5
                                if veh_d < min_d:
                                    min_d = veh_d
                                if min_d < 0:
                                    min_d = 0
                                if min_d > 1:
                                    min_d = 1

                            if min_d != 10000000:
                                veh_seqs[planner_event[0]] = [veh_seqs[seq_id][0] + (1 - min_d), veh_seqs[seq_id][1]]
                            veh_seqs[planner_event[0]] = [veh_seqs[seq_id][0], veh_seqs[seq_id][1] + 1]

                if event_path_length > 0:
                    path_len[seq_id].append(event_path_length)

                if plan_cost <= 15000:
                    path_feasbility[seq_id].append(1)
                else:
                    path_feasbility[seq_id].append(0)

            except Exception as e:
                #traceback.print_exc()
                if show_error:
                    print("RNN generated sequence parse errors in planner database ")
                    twin_info_message("RNN generated sequence parse errors in planner database ")
                show_error = False


        seq_list = list(loc_seqs.keys())
        scores = []
        for seq in seq_list:
            proximity_scenario = loc_seqs[seq][0]
            total_scenario = loc_seqs[seq][1]
            proximity_vehicles = veh_seqs[seq][0]
            total_vehicles = veh_seqs[seq][1]

            if total_scenario > 2 and total_vehicles > 2: # > 10, looking for sequences with at leasat some length, tunable
                avg_path_lengths = sum(path_len[seq])/len(path_len[seq])
                avg_path_feasiblity = sum(path_feasbility[seq])/len(path_feasbility[seq])
                scores.append(0.3*proximity_scenario/total_scenario + 0.3*proximity_vehicles/total_vehicles + 0.2*avg_path_lengths/max_path_len + 0.2*avg_path_feasiblity)
            else:
                scores.append(0)

        sorted_indices = numpy.argsort(scores)[::-1].tolist()

        # sample new events
        all_events = []
        while len(all_events) < len(self.team_time_events[usr]):
            selected_ind = max(0,int(self.linear_trend(1.0, 0.0, 0, min(20, len(sorted_indices)), 1)[0]))
            events = self.planner_sequences.query("seq == " + str(seq_list[sorted_indices[selected_ind]])).values.tolist()
            sorted_indices.pop(selected_ind)
            for event in events:
                all_events.append(event)

        self.assign_events_to_user(usr, all_events)

    def sample_business_events(self, usr):
        starting_events = self.business_sequences.query("start_submit == 1").values.tolist()
        idx = random.randrange(0, len(starting_events))
        seq_events = self.business_sequences.query("seq == " + str(starting_events[idx][0])).values.tolist()

        business_time_events = self.linear_trend(0.32, 0.68, 0, 20, len(seq_events))
        business_time_events.sort()
        self.team_role[usr] = "business"
        self.team_data[usr] = None
        self.team_time_events[usr] = business_time_events
        print(self.team_time_events[usr])
        twin_info_message(self.team_time_events[usr])
        self.assign_events_to_user(usr, seq_events)

    def sample_design_sequence_starting_open_design(self, range_vehicle, capacity_vehicle, cost_vehicle):

        target_vehicles = [[range_vehicle, capacity_vehicle, cost_vehicle]]
        closest_vehicle = self.get_closest_vehicles(target_vehicles)[0]

        start_designs = self.designer_sequences.query("start == 1")
        min_values = start_designs.min()
        max_values = start_designs.max()
        all_distances = []
        all_seq = []
        for i in start_designs.index:
            norm_distance = (((closest_vehicle.range - float(start_designs.at[i,'range']))/(max_values["range"] - min_values["range"]))**2 + \
                ((closest_vehicle.payload - float(start_designs.at[i,'capacity']))/(max_values["capacity"] - min_values["capacity"]))**2 + \
                ((closest_vehicle.cost - float(start_designs.at[i,'cost']))/(max_values["cost"] - min_values["cost"]))**2)**0.5
            all_distances.append(norm_distance)
            all_seq.append(start_designs.at[i,'seq'])
        sort_index = numpy.argsort(all_distances)

        # add randomness by to chnage 0 to something else
        seqs = []
        counter = 0
        last_tag = "tag"
        last_range = -1
        last_capacity = -1
        last_cost = -1
        last_velocity = -1
        while len(seqs) < 2:
            selected_ind = max(0,int(self.linear_trend(1.0, 0.0, 0, min(20, len(sort_index)), 1)[0]))
            seqs = self.designer_sequences.query("seq == " + str(all_seq[sort_index[selected_ind]])).values.tolist()
            for seq in seqs:
                last_range = seq[3]
                last_capacity = seq[4]
                last_cost = seq[5]
                last_velocity = seq[6]
            counter += 1

        return [seqs, closest_vehicle.tag, closest_vehicle.config, closest_vehicle.range, closest_vehicle.payload, closest_vehicle.cost,  closest_vehicle.velocity, last_range, last_capacity, last_cost]

    # get the closest session plan to the target plan metrics
    def get_close_plan(self, profit, startupCost, no_deliveries, business_role):
        close_plan = None
        closest_plan_index = -1
        closest_plan_dist = 100000000
        min_startup_cost = 100000000
        max_profit = profit
        max_startup_cost = startupCost
        max_number_deliveries = no_deliveries
        plans = self.db_helper.query_plans()
        if len(plans) > 0:
            for p in plans:
                if p.id not in self.plan_cache:
                    result = OpsService(self.convert_plan_str(p))
                    self.plan_cache[p.id] = [result.profit, result.startupCost, result.number_deliveries]
                if self.plan_cache[p.id][0] > max_profit:
                    max_profit = self.plan_cache[p.id][0]
                if self.plan_cache[p.id][1] > max_startup_cost:
                    max_startup_cost = self.plan_cache[p.id][1]
                if self.plan_cache[p.id][1] < min_startup_cost:
                    min_startup_cost = self.plan_cache[p.id][1]
                if self.plan_cache[p.id][2] > max_number_deliveries:
                    max_number_deliveries = self.plan_cache[p.id][2]

            dist_scores = []
            for p in plans:
                d = (((self.plan_cache[p.id][0] - profit)/max_profit)**2 + ((self.plan_cache[p.id][1] - startupCost)/max_startup_cost)**2 + ((self.plan_cache[p.id][2] - no_deliveries)/max_number_deliveries)**2)**0.5
                #d = ((self.plan_cache[p.id][0] - profit)/max_profit)**2 + ((self.plan_cache[p.id][1] - startupCost)/max_startup_cost)**2
                if business_role:
                    if self.plan_cache[p.id][1] > 15000:
                        d = 100000000
                dist_scores.append(d)

            # sorted indices by distance
            sorted_indices = numpy.argsort(dist_scores)
            if business_role:
                close_plan = plans[int(sorted_indices[0])]
                # make sure it is feasible
                if self.plan_cache[close_plan.id][1] > 15000 or self.plan_cache[close_plan.id][1] <= 0:
                    close_plan = None
            else:
                selected_ind = max(0,int(self.linear_trend(1.0, 0.0, 0, min(5, len(sorted_indices)), 1)[0]))
                close_plan = plans[int(sorted_indices[selected_ind])]

        return close_plan;

    # gets an RNN vehicle string
    def get_vehicle_string(self, vehicle):
        return "r" + str(int(vehicle.range)) + "c" + str(int(vehicle.payload)) + "$" + str(int(vehicle.cost))

    # converts RNN vehicle string to metrics
    def get_vehicle_metrics(self, vehicle_rep):
        range = int(vehicle_rep.split("c")[0][1:])
        capacity = int(vehicle_rep.split("c")[1].split("$")[0])
        cost = int(vehicle_rep.split("c")[1].split("$")[1])
        return [range, capacity, cost]

    # get the closest session vehicles to the target vehicles
    def get_closest_vehicles(self, target_vehicles):

        # get all available vehicles to the user
        vehicles = self.db_helper.query_vehicles()

        # get maximum bounds to use for normalized distance calculations
        max_range = -100000000000
        max_payload = -100000000000
        max_cost = -100000000000
        for v in vehicles:
            if v.range > max_range:
                max_range = v.range
            if v.payload > max_payload:
                max_payload = v.payload
            if v.cost > max_cost:
                max_cost = v.cost
        for target in target_vehicles:
            if target[0] > max_range:
                max_range = target[0]
            if target[1] > max_payload:
                max_payload = target[1]
            if target[2] > max_cost:
                max_cost = target[2]

        used_vehicles = []
        # if there are vehicles
        if len(vehicles) > 0:
            # for each target vehicle, find the closest existing vehicle
            for target in target_vehicles:
                closest_dist = 100000000
                closest_veh = None
                for v in vehicles:
                    #d =  ((target[2] - v.cost)/max_cost)**2 # use cost as an initial target to add vehicle to get near the budget constraint
                    d =  (((target[0] - v.range)/max_range)**2 + ((target[1] - v.payload)/max_payload)**2 + ((target[2] - v.cost)/max_cost)**2)**0.5
                    if d < closest_dist:
                        closest_dist = d
                        closest_veh = v
                used_vehicles.append(closest_veh)

        return used_vehicles

    # resamples events for a user after the current time
    def assign_events_to_user(self, usr, all_events):

        # remove event in action queue for this user , reverse order for removes
        action_ind_to_remove = []
        for idx, action in enumerate(self.actions_queue):
            if action[1] == usr and action[0] >= self.current_time:
                action_ind_to_remove.insert(0, idx)

        # remove all queued events
        for idx in action_ind_to_remove:
            self.actions_queue.pop(idx)

        # add all events
        counter = 0
        for time in self.team_time_events[usr]:
            if time >= self.current_time:
                self.register_action_in_queue(usr, time, all_events[counter])
                counter += 1

    # registers a new action to a queue ordered by time
    def register_action_in_queue(self, usr, time_min, action_obj ):

        # get the length of the queue
        N = len(self.actions_queue)

        # add action to the event list, either at the end, beginning, or inserted in time with other actions
        if N == 0:
            self.actions_queue.append([time_min, usr, action_obj])
        elif self.actions_queue[N - 1][0] <= time_min:
            self.actions_queue.append([time_min, usr, action_obj])
        elif self.actions_queue[0][0] > time_min:
            self.actions_queue.insert(0, [time_min, usr, action_obj])
        else:
            idx = 0
            for i in range(len(self.actions_queue)):
                if self.actions_queue[i][0] <= time_min:
                    idx = i
            self.actions_queue.insert(idx + 1, [time_min, usr, action_obj])

        valid = True
        time_check = -1
        for i in range(len(self.actions_queue)):
            if self.actions_queue[i][0] < time_check:
                valid = False
                print("error : ++++++++++++++++++++++ invalid action queue ++++++++++++++++++++++ ")
                print(self.actions_queue)
                twin_info_message("error : ++++++++++++++++++++++ invalid action queue ++++++++++++++++++++++ ")
                twin_info_message(self.actions_queue)
            time_check = self.actions_queue[i][0]

    # create integer sample from a distribution
    # similar to above, but returning a integer value instead of a bin value
    # so if the bin width has a range, all values in that range can be returned (instead of just a bin index)
    # this method randomly selects an x y position in a rectangle, and throws away points that do not
    # lie within the distribution,
    def sample_from_binned_dist(self, bin_probs, minimum, maximum):
        sample = True
        counter = 0    # prevent infinite loop (if given a inefficient list bin_probs (ex 0.0001, 0, 0.001))
        while sample and counter < 1000:
            counter += 1
            x = random.random()
            y = random.random()
            bin = min(math.floor(x*len(bin_probs)),len(bin_probs) - 1)  # get the bin of the x position
            if y <= bin_probs[bin]:                                     # if y is less than the height of the bin
                return round(minimum + x*(maximum - minimum))
        return -1

    def linear_trend(self, min_value, slope, min_range, max_range, N):
        samples = []
        while len(samples) < N:
            x = random.random()
            y = random.random()
            v = min_value + slope*x
            if y < v:                                                   # is y is less than the value of the line at the x location (under the curve)
                samples.append(min_range + x*(max_range - min_range))
        return samples

    # converts a plan object to a json object
    def convert_plan_json(self, p):
        return json.loads(self.convert_plan_str(p))

    def convert_plan_str(self, p):
        serializer = PlanSerializer(p)
        return json.dumps(serializer.data)

    # convert a json plan to a json string
    def convert_plan_json_to_str(self, plan_json):
        return json.dumps(plan_json)

    def write_designer_metrics(self, t, usr, event_type, vehicle_range, vehicle_capacity, vehicle_cost, config):
        #print("commented out")
        x = 0
        #with open("designer.txt", "a") as myfile:
        #    myfile.write(str(self.session.id) + "\t" + usr + "\t" + str(t) + "\t" + event_type + "\t" + str(vehicle_range) + "\t" + str(vehicle_capacity) + "\t" + str(vehicle_cost) + "\t" + config + "\n")
        #    myfile.close()

    def write_planner_metrics(self, t, usr, event_type, profit, startupCost, no_deliveries):
        #print("commented out")
        x = 0
        #with open("planner.txt", "a") as myfile:
        #    myfile.write(str(self.session.id) + "\t" + usr + "\t" + str(t) + "\t" + event_type + "\t" + str(profit) + "\t" + str(startupCost) + "\t" + str(no_deliveries) + "\n")
        #    myfile.close()

    def write_business_metrics(self, t, usr, event_type, profit, startupCost, no_deliveries, scenario_str = ""):
        #print("commented out")
        x = 0
        #with open("business.txt", "a") as myfile:
        #    myfile.write(str(self.session.id) + "\t" + usr + "\t" + str(t) + "\t" + event_type + "\t" + str(profit) + "\t" + str(startupCost) + "\t" + str(no_deliveries) + "\t" + str(scenario_str) + "\n")
        #    myfile.close()
