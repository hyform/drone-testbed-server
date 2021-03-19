import argparse
import os
import pandas as pd
import random
import numpy
import math
import json
import traceback
import time

from django.db.models import Subquery

from ai.models import OpsService
from exper.models import UserPosition, GroupPosition, Session, SessionTeam, Group, Market, User
from repo.models import Profile, ExperOrg, DesignTeam
from exper.models import Organization, Study, Experiment, SessionTeam, Exercise, CustomLinks
from exper.models import Structure, Role, Position, Group, GroupPosition

from ai.models import OpsService
from repo.models import Scenario, Vehicle, Plan, Customer, Path, PathCustomer, Warehouse, CustomerScenario, Address
from chat.messaging import new_plan_message
from ai.models import OpsPlan

from .database_helper import DatabaseHelper
from repo.serializers import PlanSerializer
#from .generate_role_sequences import GenerateRoleSequences

from api.messaging import twin_info_message, twin_complete_message


# initializes a team of agents based on an experimental session and then starts a team simulation in a new thread
class AdaptiveTeamAIUpdatedPlanner():

    def __init__(self):
        self.success_run = []
        print("initialize digital twin")
        twin_info_message("initialize digital twin")

    # method to run doe, keep number of runs small for now as it will clog up the experimenter page
    # need to add a flag to the experimental sessions to identify if it is a doe run
    #def doe(self, usr):
    #    start_time = time.time()
        # sometime a feasible plan is not generated for a session now, so skip those sesson and run until the desired number if reached
    #    while len(self.success_run) < 34:
    #        session = self.setup_session(usr)
    #        self.setup(session)
    #        print("time : ", len(self.success_run), time.time() - start_time)

    def setup(self, session):

        self.session = session
        self.db_helper = DatabaseHelper(session)

        self.designer_sequences = pd.read_csv(r'static/ai/ai_designer_sequences_updated.txt', sep='\t')
        self.planner_sequences = pd.read_csv(r'static/ai/ai_planner_sequences_updated.txt', sep='\t')
        self.business_sequences = pd.read_csv(r'static/ai/ai_business_sequences.txt', sep='\t')

        # should this run in real time
        self.real_time = False

        self.team_role = {}
        self.team_data = {}
        self.team_time_events = {}

        self.plan_cache = {}


        self.business_scenario_submitted = False    # flag to identify if a scenario has been submitted
        self.business_select_event = None           # variable to identify a business selected event
        self.business_selected = False              # flag to identify if the business selected a final plan

        # cisat settings, trained RNNs should have this information, but some is going to be a challenge to get (like satisficing_factor)
        self.self_bias = {}
        self.self_bias_designs = {}
        self.self_bias_plans = {}
        self.interaction_timing = {}

        # arrays to save data to visualize doe run results
        self.plan_vis_log = []
        self.business_vis_log = []
        self.designer_vis_log = []

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
                # if the designer session is assumed one event, then an Open event may correspond
                # to a design which is not close to the current team designs. As a result, following actions
                # would not make sense, so, the idea is to create individual event sequences using Start session
                # and Open events , Open sequcens are selected based on current team vehciles, and resulting event
                # sequences should correspond to the first event in the selected event sequence
            elif 'Design' in user_roles[usr]:
                # use historical human study data to select number of events and times for the designer
                number_of_designer_events_dist = [0.56, 0.625, 0.75, 1.0, 0.5, 0.437, 0.25, 0.125, 0.0625, 0.0625]
                number_of_designer_events = self.sample_from_binned_dist(number_of_designer_events_dist, 4, 75)
                designer_time_events= self.linear_trend(0.28, 0.72, 0, 20, number_of_designer_events)
                designer_time_events.sort()
                self.team_role[usr] = "designer"
                self.team_data[usr] = None
                self.team_time_events[usr] = designer_time_events
            elif 'Plan' in user_roles[usr]:
                # use historical human study data to select number of events and times for the planner
                number_of_planner_events_dist = [0.42, 0.31, 0.17, 0.07, 0.0, 0.01, 0, 0, 0, 0.01]
                number_of_planner_events = int(self.sample_from_binned_dist(number_of_planner_events_dist, 1, 180))
                planner_time_events= self.linear_trend(0.32, 0.68, 0, 20, number_of_planner_events)
                planner_time_events.sort()
                self.team_role[usr] = "planner"
                self.team_data[usr] = None
                self.team_time_events[usr] = planner_time_events

        # for now , initialize cisat parameters (0-1)
        for usr in user_roles:
            self.self_bias[usr] = 0.0
            self.interaction_timing[usr] = 1.0
            self.self_bias_designs[usr] = []
            self.self_bias_plans[usr] = []

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
                # use previous selected event
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

        # archive and save the status
        session.status = Session.ARCHIVED
        session.save()

        twin_complete_message("Final Business Plan Selected : " + str(self.business_selected))

        # return if a valid session
        return self.business_selected

    # runs a design, planner, or business action in the simulation
    def run_action(self, action):

        try:

            print("action",action)
            twin_info_message(action)

            # probably need to develop a event object, instead of using lists
            t = action[0]
            usr = action[1]
            self.current_time = t
            self.db_helper.set_user_name(usr)

            # if business event
            if self.team_role[usr] == "business":
                action_info = action[2][1].split(";")

                # for now, restricting to one scenario submit early in the session
                # that is the reason for the second condition and third condition
                if action_info[0] == "Scenario" and not self.business_scenario_submitted and t <= 2:

                    # locations to include in the scenario
                    # format of the AI is inverse to the agent code, so a bunch of string modifications
                    # my fault, need to change this
                    locations = action_info[1].replace("|",";").replace(":", "|").split(";")

                    # the historical data had lower bound of 15, so RNN generate something less that that, assume a full set of customers
                    if len(locations) >= 15:

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
                        self.cache_business_metrics(t, usr, "Scenario", number_selected, 0, 0, scenario_str)

                    else:
                        self.cache_business_metrics(t, usr, "Scenario", 56, 0, 0, "")
                        print("default scenario submit")
                        twin_info_message("default scenario submit")
                    self.business_scenario_submitted = True

                # open plan , gets all current available team plans and selects a plan with the close metrics
                if action_info[0] == "Open":
                    close_plan = self.get_close_plan(usr, float(action_info[1]),float(action_info[2]),float(action_info[3]), False)
                    if close_plan is not None:

                        # sets the data object for the business user
                        json_plan = self.convert_plan_json(close_plan)
                        self.team_data[usr] = json_plan

                        # log the event
                        plan_str = self.convert_plan_json_to_str(json_plan)
                        result = OpsService(plan_str)
                        metricstr = "Profit," + str(result.profit) + ",OperatingCost," + str(result.operating_cost) + ",StartUpCost," + str(result.startupCost) + ",Number of Deliveries," + str(result.number_deliveries) + ",MassDelivered," + str(result.total_weight_delivered) + ",Parcel," + str(result.total_parcel_delivered) + ",Food," + str(result.total_food_delivered)
                        # add datalog event
                        self.db_helper.submit_data_log(usr, "Opened;" + json_plan['tag'] + ";" + plan_str + ";" + metricstr, self.real_time, t)
                        self.cache_business_metrics(t, usr, "Open", result.profit, result.startupCost, result.number_deliveries, "")

                if action_info[0] == "Selected" and t >= 18:
                    # select business plan
                    # float(action_info[1]), float(action_info[2]), float(action_info[3]) are business suggested, but not currently
                    # corillated with the current team plan, need to adjust for this as we do for the planners
                    # in historical trend, business role almost regularly selects plan with highest profit and most number of customers
                    closest_plan = self.get_close_plan(usr, 10000, float(action_info[2]), 40, True)
                    if closest_plan is not None and not self.business_selected:

                        # json plan object
                        closest_plan_json = self.convert_plan_json(closest_plan)
                        self.business_selected = True

                        # convert to string for logging
                        plan_str = self.convert_plan_json_to_str(closest_plan_json)         # create a string representation of the plan
                        result = OpsService(plan_str)
                        metricstr = "Profit," + str(result.profit) + ",OperatingCost," + str(result.operating_cost) + ",StartUpCost," + str(result.startupCost) + ",Number of Deliveries," + str(result.number_deliveries) + ",MassDelivered," + str(result.total_weight_delivered) + ",Parcel," + str(result.total_parcel_delivered) + ",Food," + str(result.total_food_delivered)
                        # add datalog event
                        self.db_helper.submit_data_log(usr, "BusinessPlanSelected;" + closest_plan_json['tag'] + ";" + str(closest_plan_json['id']) + ";" + plan_str + ";" + metricstr, self.real_time, t)
                        self.cache_business_metrics(t, usr, "Selected", result.profit, result.startupCost, result.number_deliveries, "")
                        print("---- Business Selected ----", metricstr)
                        twin_info_message("---- Business Selected ----")
                        twin_info_message(metricstr)

                # save selected event for at the end of the session
                if action_info[0] == "Selected" and t < 18 and self.business_select_event is None:
                    self.business_select_event = action

            # if a designer event
            if self.team_role[usr] == "designer":
                # submit a design
                if action[2][2] == "Submit" and self.is_design_unique(usr, action[2][1]):
                    tag = "design:" + usr + ":" + str(t)
                    veh = self.db_helper.submit_vehicle_db(tag, action[2][1], action[2][3], action[2][4], action[2][5], action[2][6])
                    # add datalog event
                    self.db_helper.submit_data_log(usr, "SubmitToDB;" + tag + ";range=" + str(action[2][3]) + ",capacity=" + str(action[2][4]) + ",cost=" + str(action[2][5]) + ",velocity=" + str(action[2][6]), self.real_time, t)
                    self.resample_planners_based_on_scenario_and_vehicles()
                    self.cache_designer_metrics(t, usr, "Submit", action[2][3], action[2][4], action[2][5], action[2][1])
                    # add user plan
                    self.self_bias_designs[usr].append(str(veh.id))
                # open a design
                elif action[2][2] == "Open":
                    selected_vehicle_data = self.resample_designer_based_on_metrics(usr, action[2][3], action[2][4], action[2][5], False)
                    # add datalog event
                    self.db_helper.submit_data_log(usr, "Open;tag=" + selected_vehicle_data[0] + ";config=" + selected_vehicle_data[1] + ";range=" + str(selected_vehicle_data[2]) + ",capacity=" + str(selected_vehicle_data[3]) + ",cost=" + str(selected_vehicle_data[4]) + ",velocity=" + str(selected_vehicle_data[5]), self.real_time, t)
                    self.cache_designer_metrics(t, usr, "Open", selected_vehicle_data[2], selected_vehicle_data[3], selected_vehicle_data[4], selected_vehicle_data[1])
                else:   # evaluate
                    # add datalog event
                    self.db_helper.submit_data_log(usr, "Evalauted;" + action[2][2] + ";range=" + str(action[2][3]) + ",capacity=" + str(action[2][4]) + ",cost=" + str(action[2][5]) + ",velocity=" + str(action[2][6]), self.real_time, t)
                    self.cache_designer_metrics(t, usr, "Evaluated", action[2][3], action[2][4], action[2][5], action[2][1])

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

                        # calculate current plan
                        plan_str = self.convert_plan_json_to_str(self.team_data[usr])
                        result = OpsService(plan_str)
                        metrics = "Profit," + str(result.profit) + ",OperatingCost," + str(result.operating_cost) + ",StartUpCost," + str(result.startupCost) + ",Number of Deliveries," + str(result.number_deliveries) + ",MassDelivered," + str(result.total_weight_delivered) + ",Parcel," + str(result.total_parcel_delivered) + ",Food," + str(result.total_food_delivered)

                        # if profit
                        if result.profit > 0 and self.is_plan_unique(usr, result.profit, result.startupCost, result.number_deliveries):
                            p = self.db_helper.plan_submit(plan)
                            # add datalog event
                            self.db_helper.submit_data_log(usr, "SubmitPlanToDB;" + plan['tag'] + ";" + plan_str + ";" + metrics, self.real_time, self.current_time)
                            self.cache_planner_metrics(self.current_time, usr, "Submit", result.profit, result.startupCost, result.number_deliveries)

                            # add user plan to self bias list
                            self.self_bias_plans[usr].append(str(p.id))

                            print("---- Submit Plan ---- ", metrics, p.id)
                            twin_info_message("---- Submit Plan ----")
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
                    close_plan = self.get_close_plan(usr, profit, startupCost, no_deliveries, False)
                    if close_plan is not None:

                        # set plan object as a json object
                        close_plan_json = self.convert_plan_json(close_plan)
                        self.team_data[usr] = close_plan_json

                        # convert to string for log and run to get metrics
                        plan_str = self.convert_plan_json_to_str(close_plan_json)
                        result = OpsService(plan_str)
                        metrics = "Profit," + str(result.profit) + ",OperatingCost," + str(result.operating_cost) + ",StartUpCost," + str(result.startupCost) + ",Number of Deliveries," + str(result.number_deliveries) + ",MassDelivered," + str(result.total_weight_delivered) + ",Parcel," + str(result.total_parcel_delivered) + ",Food," + str(result.total_food_delivered)

                        # add datalog event
                        self.db_helper.submit_data_log(usr, "Opened;" + close_plan_json['tag'] + ";" + plan_str + ";" + metrics, self.real_time, t)
                        self.cache_planner_metrics(t, usr, "Open", result.profit, result.startupCost, result.number_deliveries)

                # runs the planner AI agent
                elif "Agent" in tokens[0]:

                    metrics = tokens[0].split("=")[1]

                    # create the plan input string with empty paths, where each path has a closest vehicle as recommended by the planner AI
                    plan = {}
                    paths = []
                    scenario_obj = self.db_helper.get_scenario()

                    # since we the planner is the adapter and the plan metrics are high, assist in meeting cost constraint
                    fixed_cost = 0

                    # get the vehicle metrics for each path and add a closest team vehicle and add an empty plan
                    deliveries = tokens[1].split("Path")
                    for delivery in deliveries:
                        if len(delivery) > 0:

                            try:
                                path_metrics = delivery.split(";")
                                vehicle_str = path_metrics[0]
                                vehiclerange = int(vehicle_str.split("c")[0][1:])
                                vehiclecapacity = int(vehicle_str.split("c")[1].split("$")[0])
                                vehiclecost = int(vehicle_str.split("c")[1].split("$")[1])

                                if fixed_cost + vehiclecost > 15000:
                                    vehiclecost = max(0, 15000 - fixed_cost)

                                used_vehicle = self.get_closest_vehicles(usr, [[vehiclerange, vehiclecapacity, vehiclecost]], False)[0]

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

                                fixed_cost += used_vehicle.cost

                            except Exception as e:
                                print(e)
                                twin_info_message(str(e))

                    # add an empty path to the plan
                    plan['paths'] = paths
                    plan['scenario'] = scenario_obj

                    # convert to string for the planner AI
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
                    self.cache_planner_metrics(t, usr, "PathAgent", result.profit, result.startupCost, result.number_deliveries)

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

                    # add variable for fixed cost
                    fixed_cost = 0

                    # get path tokens
                    add_path_tokens = tokens[1].split(";")
                    current_path = None
                    added_to_plan = False
                    for path_token in add_path_tokens:
                        # vehicle tokens have $ in the token
                        if "$" in path_token: # vehicle

                            # get the vehicle metrics from the token
                            results = self.get_vehicle_metrics(path_token)

                            # get closest fesible vehicle
                            if fixed_cost + results[2] > 15000:
                                results[2] = max(0, 15000 - results[2])

                            # get closest vehicle in the session
                            used_vehicle = self.get_closest_vehicles(usr, [[results[0], results[1], results[2]]], False)[0]

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

                            fixed_cost += used_vehicle.cost

                        # if there is a current vehicle and the token is a location
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

                            # for each customer in the selected business scenario, get its proximity to the suggestion and if it is feasible and not already included
                            for customer in scenario_obj['customers']:

                                # make sure it is included in the scenario
                                if customer['selected']:

                                    customer_x = float(customer['address']['x'])
                                    customer_z = float(customer['address']['z'])

                                    # create a new path that will append the suggestion to test before adding it to the plan
                                    append_cp_path = []
                                    already_in_path = False
                                    for customer_copy in cp_path:
                                        append_cp_path.append(customer_copy)
                                        if float(customer_copy['address']['x']) == customer_x and float(customer_copy['address']['z']) == customer_z:
                                            already_in_path = True

                                    # if the suggested location is not already in the path
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
                        self.cache_planner_metrics(t, usr, "ManualPathOperation", result.profit, result.startupCost, result.number_deliveries)


        except Exception as e:
            print("---- RNN parser error ----")
            twin_info_message("---- RNN parser error ----")
            twin_info_message(str(e))
            traceback.print_exc()
            pass

    # checks if a vehicle is unique
    def is_design_unique(self, usr, config):
        vehicles = self.db_helper.query_vehicles()
        for v in vehicles:
            if v.config == config:
                return False
        return True

    # check if the plan is unique to avoid submitting duplicate plans
    def is_plan_unique(self, usr, profit, startupCost, number_deliveries):
        plans = self.db_helper.query_plans()
        for p in self.plan_cache:
            metrics = self.plan_cache[p]
            if metrics[0] == profit and metrics[1] == startupCost and metrics[2] == number_deliveries:
                return False
        return True

    # method to generate initial events for each user
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

        # clear array to capture all events
        all_events = []
        first_event_data = None

        # set user name to view appropriate available vehicles
        self.db_helper.set_user_name(usr)

        # starting seqeunce and new session (just base vehicle)
        vehicles = self.db_helper.query_vehicles()
        if start_sequence and len(vehicles) == 1:

            starting_events = self.designer_sequences.query("type == 'Submit' and start_submit == 1").values.tolist()

            # get all event sequences with a Start event
            start_seq_ids = []
            for starting_event in starting_events:
                id_num = int(starting_event[0])
                if id_num not in start_seq_ids:
                    start_seq_ids.append(id_num)

            # select a random sequence
            idx = random.randrange(0, len(start_seq_ids))

            seq_events = []
            # get sequences of some length with evaluates
            while len(seq_events) < 3:
                seq_events = self.designer_sequences.query("seq == " + str(start_seq_ids[idx])).values.tolist()
                idx = random.randrange(0, len(starting_events))

            # at starting events to all events
            for event in seq_events:
                all_events.append(event)
                range = event[3]
                capacity = event[4]
                cost = event[5]

        # sample events with Start or Open
        if not start_sequence:
            #first_event_data = self.sample_design_sequence_starting_open_design(usr, range, capacity, cost, True)
            first_event_data = self.sample_design_sequence_starting_open_design(usr, range, capacity, cost)
            first_events = first_event_data[0]
            for event in first_events:
                all_events.append(event)

        # sample remaining events
        while len(all_events) < len(self.team_time_events[usr]):
            # selecting random sequence now, could use previous last vehicle from the previous events
            #event_data = self.sample_design_sequence_starting_open_design(usr, last_range, last_capacity, last_cost, False)
            event_data = self.sample_random_designer_sequence(usr)
            for event in event_data:
                all_events.append(event)

        # assign events to the user
        self.assign_events_to_user(usr, all_events)

        if first_event_data is not None:
            # seqs, tag, config, range, capacity, cost, velocity]
            return [first_event_data[1], first_event_data[2], first_event_data[3],first_event_data[4],first_event_data[5],first_event_data[6]  ]

    # resamples planner event for all users
    def resample_planners_based_on_scenario_and_vehicles(self):
        for usr in self.team_role:
            if self.team_role[usr] == "planner":
                self.resample_planner_based_on_scenario_and_vehicles(usr)

    # attempts to adjust planners event sequences to match the designer submintted designs and business scenarios
    def resample_planner_based_on_scenario_and_vehicles(self, usr):

        self.db_helper.set_user_name(usr)
        vehicles = self.db_helper.query_vehicles()
        scenario = self.db_helper.get_scenario()

        # get all locations in the scenario and store as string for comparison, with a profit for each customer
        locations = {}
        # add a scaling factor for profit
        for customer in scenario['customers']:
            if "food" in customer['payload']:
                locations[str(customer['address']['x']) + "," + str(customer['address']['z'])] = 200*customer['weight']
            else:
                locations[str(customer['address']['x']) + "," + str(customer['address']['z'])] = 100*customer['weight']

        # try and bias away from base vehicle to use generated designs
        current_vehicles = []
        for vehicle in vehicles:
            if len(vehicles) == 1:
                current_vehicles.append([vehicle.range, vehicle.payload, vehicle.cost])
            elif vehicle.tag != "base":
                current_vehicles.append([vehicle.range, vehicle.payload, vehicle.cost])

        # set upper limits for analysis
        max_range = 100
        max_capacity = 99
        max_cost = 15000

        # keeps track of how many locations match the locations in the submitted scenario for all events in a planner sequence
        loc_seqs = {}

        # keeps track of how many vehicles match the locations in the submitted scenario for all events in a planner sequence
        veh_seqs = {}

        # keeps track of how many plans have valid cost for all events in a planner sequence
        plan_feasbilities = {}

        # keeps track of how many customers are in the plans (this was added because the planner sequences bias to choose small
        # paths since they were feasible, this is th only non human tinkering part that needs to be addressed
        plan_no_customers = {}
        max_plan_no_customers = 0

        # for future preference bias
        plan_profit_values = {}
        max_profit = 0
        plan_cost_values = {}
        max_plan_cost = 0

        # the RNN is not perfect, so it generated events that do not conform to the grammar, so on show one error
        # to prevent overflow in the terminal
        show_error = True
        # each event is a Start session, long string representing opening a plan, manually generating a plan, or and planner AI agent result
        # or a submit operation
        for planner_event in self.planner_sequences.values.tolist():
            try:

                # quick estimate of plan metrics without full analysis for feasbility
                plan_customers = 0
                plan_cost = 0
                plan_profit = 0

                # gets the sequence id, if this is the first one with this id, we need to initialize
                # its values in the above maps
                location_tokens = planner_event[1].split(";")
                seq_id = planner_event[0]
                if seq_id not in loc_seqs:
                    loc_seqs[seq_id] = [0, 0]
                if seq_id not in veh_seqs:
                    veh_seqs[seq_id] = [0, 0]
                if seq_id not in plan_no_customers:
                    plan_no_customers[seq_id] = []
                if seq_id not in plan_feasbilities:
                    plan_feasbilities[seq_id] = []

                # if it has path information (Open, Manual, Agent)
                if len(location_tokens) > 1:
                    for i in range(len(location_tokens)):
                        # look for location tokens , with three tokens split using , x , z, weight and no $ in token that identifies a vehicle
                        location_tokens_test = location_tokens[i].split(",")
                        if (len(location_tokens_test) == 2 or len(location_tokens_test) == 3) and "$" not in location_tokens_test:

                            try:
                                # get position
                                x = location_tokens_test[0]
                                z = location_tokens_test[1]
                                loc_token = x + "," + z

                                # test if it is in the submitted scenario by the business role, if so, increment that it is valid
                                if loc_token in locations:
                                    plan_profit += locations[loc_token]
                                    loc_seqs[planner_event[0]] = [loc_seqs[seq_id][0] + 1, loc_seqs[seq_id][1]]
                                # increment the total number of locations (valid or not)
                                loc_seqs[planner_event[0]] = [loc_seqs[seq_id][0], loc_seqs[seq_id][1] + 1]

                                # increment plan customers , maybe should move this to only include for valid locations,
                                # but this plan are used as suggestions, so invalid locations should turn into closest valid locations
                                plan_customers += 1
                                if plan_customers > max_plan_no_customers:
                                    max_plan_no_customers = plan_customers

                            except Exception as f:
                                print(f)
                                twin_info_message(str(f))
                        # if the token has a $, this represents a vehicle
                        if "$" in location_tokens[i]:
                            # remove the Manual and Path tags in some of the event sequences (my fault or bug, because I did not add a delimmaor in the training data)
                            token_test = location_tokens[i].replace("Manual","")
                            if "Path" in token_test:
                                token_test = token_test.split("Path")[1]
                            token_test = token_test.replace("_","")

                            # get the drone vehicle metrics
                            metrics = self.get_vehicle_metrics(token_test)

                            # increment the plan fixed cost by the cost of the vehicle
                            plan_cost += metrics[2]

                            # get closest distance metric of a vehicle in the current team
                            min_d = 10000000
                            for veh in current_vehicles:
                                veh_d = (((veh[0] - metrics[0])/max_range)**2 + ((veh[1] - metrics[1])/max_capacity)**2 + ((veh[2] - metrics[2])/max_cost)**2)**0.5
                                if veh_d < min_d:
                                    min_d = veh_d
                                if min_d < 0:
                                    min_d = 0
                                if min_d > 1:
                                    min_d = 1
                            # add a bonus of near one for a close vehicle
                            if min_d != 10000000:
                                veh_seqs[planner_event[0]] = [veh_seqs[seq_id][0] + (1 - min_d), veh_seqs[seq_id][1]]

                            # increment the total vehicles by 1
                            veh_seqs[planner_event[0]] = [veh_seqs[seq_id][0], veh_seqs[seq_id][1] + 1]

                # add number of customer for this event
                if plan_customers > 0:
                    plan_no_customers[seq_id].append(plan_customers)

                # add a 1 if this event is feasible
                if plan_cost <= 15000:
                    plan_feasbilities[seq_id].append(1)
                else:
                    plan_feasbilities[seq_id].append(0)

                # the below will be used for upcoming preference
                plan_profit_values[seq_id] = plan_profit
                if plan_profit > max_profit:
                    max_profit = plan_profit

                plan_cost_values[seq_id] = plan_cost
                if plan_cost > max_plan_cost:
                    max_plan_cost = plan_cost

            except Exception as e:
                # fix this to check and make sure that important errors are not overlooked , which has been done, but
                # this needs updated
                #traceback.print_exc()
                if show_error:
                    print("RNN generated sequence parse errors in planner database " , str(e))
                    twin_info_message("RNN generated sequence parse errors in planner database")
                    twin_info_message(str(e))
                show_error = False


        # score all plan sequences based on proximity of vehicles to team vehicles and deleivery path locations
        seq_list = list(loc_seqs.keys())
        scores = []
        for seq in seq_list:
            proximity_scenario = loc_seqs[seq][0]
            total_scenario = loc_seqs[seq][1]
            proximity_vehicles = veh_seqs[seq][0]
            total_vehicles = veh_seqs[seq][1]

            # score event sequnce based on similarity
            event_score = 0
            if total_scenario > 2 and total_vehicles > 2: # > 10, looking for sequences with at leasat some length, tunable
                avg_plan_no_customers = sum(plan_no_customers[seq])/len(plan_no_customers[seq])
                avg_path_feasiblity = sum(plan_feasbilities[seq])/len(plan_feasbilities[seq])
                #event_score = 0.25*proximity_scenario/total_scenario + 0.25*proximity_vehicles/total_vehicles + 0.32*avg_plan_no_customers/max_plan_no_customers + 0.18*avg_path_feasiblity
                # had to add metric for feasbility and noumber of customers, which I would like to improve
                event_score = 0.25*proximity_scenario/total_scenario + 0.25*proximity_vehicles/total_vehicles + 0.35*avg_plan_no_customers/max_plan_no_customers + 0.15*avg_path_feasiblity

            # add score
            scores.append(event_score)

        # sort sequnces based on proximity
        sorted_indices = numpy.argsort(scores)[::-1].tolist()

        # sample new events
        all_events = []
        total_path_seqs = []
        total_open_seqs = []

        # fill up user events with sequences bias by score
        while len(all_events) < len(self.team_time_events[usr]):
            selected_ind = max(0,int(self.linear_trend(1.0, 0.0, 0, min(20, len(sorted_indices)), 1)[0]))
            seq_id = str(seq_list[sorted_indices[selected_ind]])
            events = self.planner_sequences.query("seq == " + seq_id).values.tolist()
            sorted_indices.pop(selected_ind)

            # check for interaction timining
            if 'Open' not in events[0][1]:
                total_path_seqs.append(seq_id)
                for event in events:
                    all_events.append(event)
            else:
                if len(total_path_seqs) > 0:
                    if 1.0*len(total_open_seqs)/len(total_path_seqs) <= self.interaction_timing[usr]:
                        total_open_seqs.append(seq_id)
                        for event in events:
                            all_events.append(event)

        # assign to user
        self.assign_events_to_user(usr, all_events)

    # selects all business role events by selecting a random event sequence
    def sample_business_events(self, usr):

        # gets event sequences that start with a scenario submit
        #starting_events = self.business_sequences.query("start_submit == 1").values.tolist()
        starting_events = self.business_sequences.values.tolist()

        # randomly choose one of them
        selected_ind = random.randrange(0, len(starting_events))
        seq_events = self.business_sequences.query("seq == " + str(starting_events[selected_ind][0])).values.tolist()

        # assign timestamps to each event
        business_time_events = self.linear_trend(0.32, 0.68, 0, 20, len(seq_events))
        business_time_events.sort()
        self.team_role[usr] = "business"
        self.team_data[usr] = None
        self.team_time_events[usr] = business_time_events

        # assign event to the user
        self.assign_events_to_user(usr, seq_events)

    # sample a random designer event sequence
    def sample_random_designer_sequence(self, usr):

        # get all starting designer sequences
        start_designs = self.designer_sequences.query("start == 1")
        all_seq = []
        for i in start_designs.index:
            all_seq.append(start_designs.at[i,'seq'])

        seqs = []
        while len(seqs) < 1:
            # randomly select one and add all events
            selected_ind = random.randrange(0, len(all_seq))
            seqs = self.designer_sequences.query("seq == " + str(all_seq[selected_ind])).values.tolist()
            for seq in seqs:
                last_range = seq[3]
                last_capacity = seq[4]
                last_cost = seq[5]
                last_velocity = seq[6]

        return seqs


    def sample_design_sequence_starting_open_design(self, usr, range_vehicle, capacity_vehicle, cost_vehicle):

        # get closest visible vehicle
        target_vehicle = [[range_vehicle, capacity_vehicle, cost_vehicle]]
        closest_vehicle = self.get_closest_vehicles(usr, target_vehicle, True)[0]

        # old code just to keep in case
        #if random.random() < self.interaction_timing[usr] or fixed_open_event:
            # get all starting events
        #else:
            # get are start session events
        #    start_designs = self.designer_sequences.query("start == 1 and type != 'Open'")

        # get all sequences that have a start or open event , if start essentially it opens the base design
        start_designs = self.designer_sequences.query("start == 1")

        # score each sequence based on proximity to the suggested closest design
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

        # list for events
        seqs = []
        counter = 0
        last_tag = "tag"
        last_range = -1
        last_capacity = -1
        last_cost = -1
        last_velocity = -1
        while len(seqs) < 1:
            # origianlly was 20, but increased to length of the sorted index to bias
            #selected_ind = max(0,int(self.linear_trend(1.0, 0.0, 0, len(sort_index), 1)[0]))
            # take away bias and choose random for now to try and match historical designer designer_trends
            selected_ind = random.randrange(0, len(sort_index))
            seqs = self.designer_sequences.query("seq == " + str(all_seq[sort_index[selected_ind]])).values.tolist()
            for seq in seqs:
                last_range = seq[3]
                last_capacity = seq[4]
                last_cost = seq[5]
                last_velocity = seq[6]
            counter += 1

        return [seqs, closest_vehicle.tag, closest_vehicle.config, closest_vehicle.range, closest_vehicle.payload, closest_vehicle.cost, closest_vehicle.velocity, last_range, last_capacity, last_cost]

    # get the closest session plan to the target plan metrics
    def get_close_plan(self, usr, profit, startupCost, no_deliveries, business_role):

        # should be already set, but need to make sure
        self.db_helper.set_user_name(usr)

        # initial variables to store and test closest plan
        close_plan = None
        closest_plan_index = -1
        closest_plan_dist = 100000000
        min_startup_cost = 100000000
        max_profit = profit
        max_startup_cost = startupCost
        max_number_deliveries = no_deliveries
        plans = self.db_helper.query_plans()

        # if there are visible plans for this user
        if len(plans) > 0:
            for p in plans:

                # if not in the cache, evaluate it
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

            # calculate the proximity for each plan
            dist_scores = []
            for p in plans:
                d = (((self.plan_cache[p.id][0] - profit)/max_profit)**2 + ((self.plan_cache[p.id][1] - startupCost)/max_startup_cost)**2 + ((self.plan_cache[p.id][2] - no_deliveries)/max_number_deliveries)**2)**0.5
                # add penaly for the fixed cost constraint
                if business_role:
                    if self.plan_cache[p.id][1] > 15000:
                        d = 100000000
                else:
                    # substract for self bias
                    if str(p.id) in self.self_bias_plans[usr]:
                        d -= self.self_bias[usr]
                dist_scores.append(d)

            # sorted indices by distance
            sorted_indices = numpy.argsort(dist_scores)
            if business_role:
                close_plan = plans[int(sorted_indices[0])]
                # make sure it is feasible
                if self.plan_cache[close_plan.id][1] > 15000 or self.plan_cache[close_plan.id][1] <= 0:
                    close_plan = None
            else:
                # biad selection based on proximity
                selected_ind = max(0,int(self.linear_trend(1.0, 0.0, 0, min(5, len(sorted_indices)), 1)[0]))
                close_plan = plans[int(sorted_indices[selected_ind])]

        return close_plan

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
    def get_closest_vehicles(self, usr, target_vehicles, bias_from_base_design):

        # get all available vehicles to the user
        vehicles = self.db_helper.query_vehicles()

        used_vehicles = []
        # if there are vehicles
        if len(vehicles) > 0:

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

            # for each target vehicle, find the closest existing vehicle
            for target in target_vehicles:
                closest_dist = 100000000
                closest_veh = None
                for v in vehicles:
                    d =  (((target[0] - v.range)/max_range)**2 + ((target[1] - v.payload)/max_payload)**2 + ((target[2] - v.cost)/max_cost)**2)**0.5

                    # subtract self-bias
                    if str(v.id) in self.self_bias_designs[usr]:
                        d -= self.self_bias[usr]

                    # bias off base design
                    if v.range == 10 and v.payload == 5 and bias_from_base_design:
                        d += 2

                    # if closest
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
            time_check = self.actions_queue[i][0]

    # create integer sample from a distribution
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

    # return N samples that match a linear trend (for timed events of agents)
    def linear_trend(self, min_value, slope, min_range, max_range, N):
        samples = []
        while len(samples) < N:
            x = random.random()
            y = random.random()
            v = min_value + slope*x
            if y < v:                                                   # is y is less than the value of the line at the x location (under the curve)
                samples.append(min_range + x*(max_range - min_range))
        return samples

    # create a new session for doe runs
    def setup_session(self, usr, unit_structure = 1, market = 1, ai = 1):

        twin_info_message("setup")
        twin_info_message("unit structure : " + str(unit_structure))
        twin_info_message("market : " + str(market))
        twin_info_message("ai : " + str(ai))

        experiment = usr.profile.experiment
        newExercise = Exercise.objects.create(experiment=experiment)

        team = DesignTeam.objects.filter(id=2).first()
        sessionName = "digital_twin_" + str(time.time())
        if ai == 1:
            sessionUseAI = True
        else:
            sessionUseAI = False
        sessionStructureId = unit_structure
        sessionStructure = Structure.objects.filter(id=sessionStructureId).first()
        sessionMarketId = market
        sessionMarket = Market.objects.filter(id=sessionMarketId).first()
        newSession = Session.objects.create(name=sessionName, experiment=experiment, exercise=newExercise, index=1, prior_session=None, structure=sessionStructure, market=sessionMarket, use_ai=sessionUseAI, status=4)
        sessionTeam = SessionTeam.objects.create(team=team, session=newSession)
        structurePositions = list(Position.objects.filter(structure=sessionStructure).order_by('name'))

        profiles = Profile.objects.filter(team=team)
        teamUsers = list(User.objects.filter(id__in=Subquery(profiles.values('user'))).order_by('username'))
        numUsers = len(teamUsers)

        numPos = len(structurePositions)
        positer = numUsers
        if numPos < positer:
            positer = numPos
        for x in range(positer):
            UserPosition.objects.create(position=structurePositions[x], user=teamUsers[x], session=newSession)

        warehouseAddress = Address.objects.filter(region="warehouse").first()
        warehouseGroup = Group.objects.filter(name="All", structure=sessionStructure).first()
        Warehouse.objects.create(address=warehouseAddress, group=warehouseGroup, session=newSession)

        baseConfig = "*aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3"
        Vehicle.objects.create(tag="base", config=baseConfig, result="Success", range=10.0, velocity=20.0, cost=3470.20043945312, payload=5, group=warehouseGroup, session=newSession)
        print("session vehicle add")
        twin_info_message("session vehicle add")

        return newSession

    # converts a plan object to a json object
    def convert_plan_json(self, p):
        return json.loads(self.convert_plan_str(p))

    # converts a plan to a string
    def convert_plan_str(self, p):
        serializer = PlanSerializer(p)
        return json.dumps(serializer.data)

    # convert a json plan to a json string
    def convert_plan_json_to_str(self, plan_json):
        return json.dumps(plan_json)

    # cache results and export to a data file
    def cache_designer_metrics(self, t, usr, event_type, vehicle_range, vehicle_capacity, vehicle_cost, config):
        self.designer_vis_log.append(str(self.session.id) + "\t" + usr + "\t" + str(t) + "\t" + event_type + "\t" + str(vehicle_range) + "\t" + str(vehicle_capacity) + "\t" + str(vehicle_cost) + "\t" + config + "\n")

    def cache_planner_metrics(self, t, usr, event_type, profit, startupCost, no_deliveries):
        self.plan_vis_log.append(str(self.session.id) + "\t" + usr + "\t" + str(t) + "\t" + event_type + "\t" + str(profit) + "\t" + str(startupCost) + "\t" + str(no_deliveries) + "\n")

    def cache_business_metrics(self, t, usr, event_type, profit, startupCost, no_deliveries, scenario_str = ""):
        self.business_vis_log.append(str(self.session.id) + "\t" + usr + "\t" + str(t) + "\t" + event_type + "\t" + str(profit) + "\t" + str(startupCost) + "\t" + str(no_deliveries) + "\t" + str(scenario_str) + "\n")
