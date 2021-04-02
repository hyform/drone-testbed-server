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
from django.db.models import Q

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

from exper.models import DigitalTwin, DigitalTwinPreference
from api.messaging import twin_info_message, twin_pref_message, twin_complete_message


# initializes a team of agents based on an experimental session and then starts a team simulation in a new thread
class AdaptiveTeamAIUpdatedPlanner():

    def __init__(self):
        self.success_run = []
        self.MINVALUE = 0
        self.MAXVALUE = 1000000
        self.pause_segment = 0
        self.pause_interval = self.MAXVALUE
        self.NOPREFERENCE = 0
        print("initialize digital twin analysis")

    def setup_with_pause_interval(self, session, pause_interval):
        self.pause_interval = pause_interval
        self.setup(session)

    def setup(self, session):

        self.session = session
        self.db_helper = DatabaseHelper(session)

        # once the approach becomes fixed, convert this to our database
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

        # initialize preference to empty in not already done using API
        #self.set_preference(session, self.preference_example())

        # sample initial events
        self.generate_initial_events()

        # start session
        self.session.status = Session.ARCHIVED
        self.session.save()


        # run simulation
        while current_action_index < len(self.actions_queue):

            # get the time
            t = self.actions_queue[current_action_index][0]
            if math.floor(t / self.pause_interval) > self.pause_segment and current_action_index < len(self.actions_queue) - 1:    # add a special condition for the last event (ex 20 minute session)
                self.pause_segment += 1
                self.session.status = Session.PAUSED
                self.session.save()

            # keep this here for paused sessions to resume
            status_check = Session.RUNNING
            try:
                status_check =  Session.objects.filter(Q(id=self.session.id)).first().status
            except Exception as e:
                print(e)

            if status_check != Session.PAUSED:
                self.run_action(self.actions_queue[current_action_index])
                current_action_index += 1
            else:
                time.sleep(1)
                twin_info_message(self.session.id, "session_paused : segment " + str(self.pause_segment + 1) + " : go ahead and do something")

        # export to data log for debugging
        #self.export_log_data_for_visualization()

        # archive session
        self.session.status = Session.ARCHIVED
        self.session.save()

        print("completed")
        twin_complete_message(self.session.id, "digital twin : completed")


    # runs a design, planner, or business action in the simulation
    def run_action(self, action):

        try:

            # probably need to develop a event object, instead of using lists
            t = action[0]
            usr = action[1]

            # send message to a channel
            twin_info_message(self.session.id, "running : time=" + str(action[0])[:6] + " : " + usr + " : " + str(action[2][1]))
            print("running : time=" + str(action[0])[:6] + " : " + usr + " : " + str(action[2][1]))

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

                    # the historical data had lower bound of 15, so if RNN generates something less that that, assume a full set of customers
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
                            closestDistance = self.MAXVALUE
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
                        twin_info_message(self.session.id, "default scenario submit")
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

                if action_info[0] == "Selected" and t >= 19.9:  # there should be a business selected event at time 20
                    # select business plan
                    closest_plan = self.get_close_plan(usr, float(action_info[1]), float(action_info[2]), float(action_info[3]), True)
                    print("closest_plan", closest_plan)
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
                        twin_info_message(self.session.id, "---- Final Business Plan Selected ----")
                        twin_info_message(self.session.id, metricstr)

            # if a designer event
            if self.team_role[usr] == "designer":
                # submit a design
                if action[2][2] == "Submit" and self.is_design_unique(usr, action[2][1]):
                    tag = "design:" + usr + ":" + str(t)
                    veh = self.db_helper.submit_vehicle_db(tag, action[2][1], action[2][3], action[2][4], action[2][5], action[2][6])
                    # add datalog event
                    self.db_helper.submit_data_log(usr, "SubmitToDB;" + tag + ";range=" + str(action[2][3]) + ",capacity=" + str(action[2][4]) + ",cost=" + str(action[2][5]) + ",velocity=" + str(action[2][6]), self.real_time, t)
                    #self.resample_planners_based_on_scenario_and_vehicles()
                    self.cache_designer_metrics(t, usr, "Submit", action[2][3], action[2][4], action[2][5], action[2][1])
                    # add user plan
                    self.self_bias_designs[usr].append(str(veh.id))
                # open a design
                elif action[2][2] == "Open":
                    # get the closest database design to the suggested
                    closest_vehicles, closest_dist = self.get_closest_vehicles(usr, [[action[2][3], action[2][4], action[2][5]]], True)
                    closest_vehicle = closest_vehicles[0]

                    # how close is it
                    closest_dist = ((((action[2][3] - closest_vehicle.range)/100)**2 + \
                        ((action[2][4] - closest_vehicle.payload)/100)**2 + \
                        ((action[2][5] - closest_vehicle.cost)/15000)**2)**0.5)/1.73

                    # is there an event seqeunce close enough, if not, "Open the base design"
                    selected_vehicle_data = []
                    if closest_dist < 0.05:
                        selected_vehicle_data = self.sample_designer(usr, 1, closest_vehicle.range, closest_vehicle.payload, closest_vehicle.cost)
                    else:
                        selected_vehicle_data = self.sample_designer(usr, -1, 10, 5, 3470) # -1 , all sequences near the base design (Open or reset design)

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
                            twin_info_message(self.session.id, "---- Submit Plan ----")
                            twin_info_message(self.session.id, metrics)
                        else:
                            print("plan had zero profit : not submitting")
                            twin_info_message(self.session.id, "plan had zero profit : not submitting")

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

                                used_vehicles, closest_dist = self.get_closest_vehicles(usr, [[vehiclerange, vehiclecapacity, vehiclecost]], False)
                                used_vehicle = used_vehicles[0]

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
                                twin_info_message(self.session.id, str(e))

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
                            used_vehicles, closest_dist = self.get_closest_vehicles(usr, [[results[0], results[1], results[2]]], False)
                            used_vehicle = used_vehicles[0]

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
                            clostest_distance = self.MAXVALUE

                            # copy path, might not need this, wanted to make sure references from original are removed
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
            twin_info_message(self.session.id, "---- RNN parser error ----")
            twin_info_message(self.session.id, str(e))
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
                self.sample_designer(usr, 0, 10, 5, 3470)
            elif self.team_role[usr] == "planner":
                self.sample_planner(usr)
            elif self.team_role[usr] == "business":
                self.sample_business(usr)

    # sample business
    def sample_business(self, usr):

        # get preference and requirement information
        # default to no preference and requirements
        pref_type = -1
        profit_preference = self.NOPREFERENCE
        fixed_cost_preference = self.NOPREFERENCE
        no_customers_preference = self.NOPREFERENCE
        min_profit = self.MINVALUE
        max_profit = self.MAXVALUE
        min_fixed_cost = self.MINVALUE
        max_fixed_cost = self.MAXVALUE
        min_no_customers = self.MINVALUE
        max_no_customers = self.MAXVALUE

        # check for preference and requirements
        user_position = self.db_helper.get_user_positions()[usr]
        digital_twin = DigitalTwin.objects.filter(user_position=user_position).first()
        if digital_twin is not None:

            twin_preference = DigitalTwinPreference.objects.filter(Q(digital_twin=digital_twin)&Q(name="profit")).first()
            if twin_preference is not None:
                profit_preference = twin_preference.pref_value
                pref_type = twin_preference.pref_type # need to check if others are the same

            twin_preference = DigitalTwinPreference.objects.filter(Q(digital_twin=digital_twin)&Q(name="fixed_cost")).first()
            if twin_preference is not None:
                fixed_cost_preference = twin_preference.pref_value
                pref_type = twin_preference.pref_type

            twin_preference = DigitalTwinPreference.objects.filter(Q(digital_twin=digital_twin)&Q(name="no_customers")).first()
            if twin_preference is not None:
                no_customers_preference = twin_preference.pref_value
                pref_type = twin_preference.pref_type

        # there is probably some pandas query for this, but this will work
        # for now, use only sequences that use selected events for the last event in the sequence, assuming that some of the
        # trianing data had incorrect select event where maybe the user did not want to select it
        all_events = self.business_sequences.drop_duplicates(subset=['seq'], keep='last').values.tolist()
        all_selected = []
        for event in all_events:
            if "Selected" in event[1]:
                all_selected.append(event)

        # get the maximum data bounds to use to score
        max_profit_data = profit_preference
        max_fixed_cost_data = fixed_cost_preference
        max_no_deliveries_data = no_customers_preference
        for event in all_selected:
            metrics = event[1].split(";")
            profit = float(metrics[1])
            fixed_cost = float(metrics[2])
            no_customers = float(metrics[3])
            if profit > max_profit_data:
                max_profit_data = profit
            if fixed_cost > max_fixed_cost_data:
                max_fixed_cost_data = fixed_cost
            if no_customers > max_no_deliveries_data:
                max_no_deliveries_data = no_customers

        all_distances = []
        for event in all_selected:
            metrics = event[1].split(";")
            profit = float(metrics[1])
            fixed_cost = float(metrics[2])
            no_customers = float(metrics[3])
            score = 0
            if pref_type == 0:
                score = -(profit_preference*profit/max_profit_data + fixed_cost_preference*fixed_cost/max_fixed_cost_data + no_customers_preference*no_customers/max_no_deliveries_data)
            elif pref_type == 1:
                score = ((((profit - profit_preference)/max_profit_data)**2 + ((fixed_cost - fixed_cost_preference)/max_fixed_cost_data)**2 + ((no_customers - no_customers_preference)/max_no_deliveries_data)**2)**0.5)/1.73

            all_distances.append(score)
            #self.cache_business_metrics(score, "foo", "foo", profit, fixed_cost, no_customers)


        sort_index = numpy.argsort(all_distances)

        # if preference or requirement is specified, if not, just randomly select a sequence
        if (profit_preference == self.NOPREFERENCE and
                fixed_cost_preference == self.NOPREFERENCE and
                no_customers_preference == self.NOPREFERENCE):
            selected_ind = random.randrange(0, len(sort_index))
        else:
            selected_ind = max(0,int(self.linear_trend(1.0, 0.0, 0, min(20, len(sort_index)), 1)[0]))

        seq_id = all_selected[sort_index[selected_ind]]
        seq_events = self.business_sequences.query("seq == " + str(seq_id)).values.tolist()

        # assign timestamps to each event
        business_time_events = self.linear_trend(0.32, 0.68, 0, 20, len(seq_events))
        business_time_events.sort()

        # make the last selected event at 20 min
        business_time_events[len(business_time_events) - 1] = 20

        # move last scenario submit to top, assume fixed scenario for the digital twin
        submit_event = None
        for seq_event in seq_events:
            if "Scenario" in seq_event[1]:
                submit_event = seq_event
        if submit_event is not None:
            seq_events[0] = [submit_event[0], submit_event[1], submit_event[2]]


        # set the last submit scenario to the first event

        self.team_role[usr] = "business"
        self.team_data[usr] = None
        self.team_time_events[usr] = business_time_events

        # assign event to the user
        self.assign_events_to_user(usr, seq_events)


    # sample planner
    def sample_planner(self, usr):

        # get preference and requirement information
        # default to no preference and requirements
        pref_type = -1
        profit_preference = self.NOPREFERENCE
        fixed_cost_preference = self.NOPREFERENCE
        no_customers_preference = self.NOPREFERENCE

        # check for preference and requirements
        user_position = self.db_helper.get_user_positions()[usr]
        digital_twin = DigitalTwin.objects.filter(user_position=user_position).first()
        if digital_twin is not None:

            twin_preference = DigitalTwinPreference.objects.filter(Q(digital_twin=digital_twin)&Q(name="profit")).first()
            if twin_preference is not None:
                profit_preference = twin_preference.pref_value
                pref_type = twin_preference.pref_type # need to check if others are the same

            twin_preference = DigitalTwinPreference.objects.filter(Q(digital_twin=digital_twin)&Q(name="fixed_cost")).first()
            if twin_preference is not None:
                fixed_cost_preference = twin_preference.pref_value
                pref_type = twin_preference.pref_type

            twin_preference = DigitalTwinPreference.objects.filter(Q(digital_twin=digital_twin)&Q(name="no_customers")).first()
            if twin_preference is not None:
                no_customers_preference = twin_preference.pref_value
                pref_type = twin_preference.pref_type

        self.db_helper.set_user_name(usr)
        vehicles = self.db_helper.query_vehicles()
        scenario = self.db_helper.get_scenario()
        # get all locations in the scenario and store as string for comparison, with a profit for each customer
        locations = {}
        # add a scaling factor for profit
        for customer in scenario['customers']:
            if customer['selected']:
                if "food" in customer['payload']:
                    locations[str(customer['address']['x']) + "," + str(customer['address']['z'])] = 200*customer['weight']
                else:
                    locations[str(customer['address']['x']) + "," + str(customer['address']['z'])] = 100*customer['weight']


        plan_profit = {}
        plan_fixed_cost = {}
        plan_no_customers = {}
        plan_actions = {}
        plan_vehicle_proximity = {}

        max_plan_profit = 0
        max_plan_cost = 0
        max_plan_no_customers = 0

        # the RNN is not perfect, so it generated events that do not conform to the grammar, so on show one error
        # to prevent overflow in the terminal
        show_error = True
        # each event is a Start session, long string representing opening a plan, manually generating a plan, or and planner AI agent result
        # or a submit operation
        for planner_event in self.planner_sequences.values.tolist():
            try:

                # quick estimate of plan metrics without full analysis for feasbility
                no_customers = 0
                cost = 0
                profit = 0

                # gets the sequence id, if this is the first one with this id, we need to initialize
                # its values in the above maps
                location_tokens = planner_event[1].split(";")
                seq_id = planner_event[0]
                if seq_id not in plan_no_customers:
                    plan_no_customers[seq_id] = []
                    plan_profit[seq_id] = []
                    plan_fixed_cost[seq_id] = []
                    plan_actions[seq_id] = []
                    plan_vehicle_proximity[seq_id] = []

                # if it has path information (Open, Manual, Agent)
                if len(location_tokens) > 1:
                    for i in range(len(location_tokens)):
                        # look for location tokens , with three tokens split using , x , z, weight and no $ in token that identifies a vehicle
                        location_tokens_test = location_tokens[i].split(",")
                        if (len(location_tokens_test) == 2 or len(location_tokens_test) == 3) and "$" not in location_tokens[i]:

                            try:
                                # get position
                                x = location_tokens_test[0]
                                z = location_tokens_test[1]
                                loc_token = x + "," + z

                                if loc_token in locations:
                                    profit += locations[loc_token]

                                    # increment plan customers ,include for valid locations,
                                    no_customers += 1
                                    if no_customers > max_plan_no_customers:
                                        max_plan_no_customers = no_customers

                            except Exception as f:
                                print(f)
                                twin_info_message(self.session.id, str(f))
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
                            cost += metrics[2]

                            # vehicle proximity, need to build this knowledge into the action
                            min_veh_d = self.MAXVALUE
                            for veh_test in vehicles:
                                vehicle_proximity = ((((metrics[0] - veh_test.range)/100)**2 +
                                        ((metrics[1] - veh_test.payload)/100)**2 +
                                        ((metrics[2] - veh_test.cost)/15000)**2)**0.5)/1.73
                                if vehicle_proximity > 1.0:
                                    vehicle_proximity = 1.0
                                if vehicle_proximity < min_veh_d:
                                    min_veh_d = vehicle_proximity
                            plan_vehicle_proximity[seq_id].append(min_veh_d)


                if profit > 0:
                    # save plan values for all sequences
                    plan_no_customers[seq_id].append(no_customers)
                    plan_profit[seq_id].append(profit)
                    if profit > max_plan_profit:
                        max_plan_profit = profit
                    plan_fixed_cost[seq_id].append(cost)
                    if cost > max_plan_cost:
                        max_plan_cost = cost

                    if "Open" in planner_event[1]:
                        plan_actions[seq_id].append("Open")
                    elif "Agent" in planner_event[1]:
                        plan_actions[seq_id].append("Agent")
                    elif "Manual" in planner_event[1]:
                        plan_actions[seq_id].append("Manual")
                    else:
                        plan_actions[seq_id].append("Other")


            except Exception as e:
                # make sure that important errors are not overlooked using traceback, but once the code runs well, do not show
                # RNN sample errors
                # this needs updated
                #traceback.print_exc()
                if show_error:
                    print("RNN generated sequence parse errors in planner database " , str(e))
                    twin_info_message(self.session.id, "RNN generated sequence parse errors in planner database")
                    twin_info_message(self.session.id, str(e))
                show_error = False


        # score all plan sequences
        seq_list = list(plan_profit.keys())
        scores = []
        for seq in seq_list:

            avg_plan_score_by_seq = 0
            seq_no_plans = len(plan_profit[seq])
            seq_plan_action = 0

            # vehicle proximity score, to get plans sequences with similar vehicles
            veh_proximities = plan_vehicle_proximity[seq]
            if len(veh_proximities) > 0:
                veh_proximity_proportion = sum(veh_proximities)/len(veh_proximities)
            else:
                veh_proximity_proportion = 0


            for i in range(seq_no_plans):

                plan_profit_seq = plan_profit[seq][i]
                plan_fixed_cost_seq = plan_fixed_cost[seq][i]
                plan_no_customers_seq = plan_no_customers[seq][i]
                plan_action_seq = plan_actions[seq][i]

                # score plan based on preference
                score = 0

                if pref_type == 0:
                    score = -(profit_preference*plan_profit_seq/max_plan_profit + fixed_cost_preference*plan_fixed_cost_seq/max_plan_cost + no_customers_preference*plan_no_customers_seq/max_plan_no_customers)
                elif pref_type == 1:
                    score = ((((plan_profit_seq - profit_preference)/max_plan_profit)**2 + ((plan_fixed_cost_seq - fixed_cost_preference)/max_plan_cost)**2 + ((plan_no_customers_seq - no_customers_preference)/max_plan_no_customers)**2)**0.5)/1.73

                # get average score
                avg_plan_score_by_seq += score/seq_no_plans

                # increment this
                if "Manual" in plan_action_seq or "Agent" in plan_action_seq:
                    seq_plan_action += 1


            # check for some kind of path actions
            if seq_plan_action > 0:
                scores.append(0.5*veh_proximity_proportion + avg_plan_score_by_seq)
            else:
                scores.append(self.MAXVALUE)

        # sort sequnces based on proximity
        sorted_indices = numpy.argsort(scores).tolist()

        # sample new events
        all_events = []

        # fill up user events with sequences bias by score
        while len(all_events) < len(self.team_time_events[usr]):
            selected_ind = max(0,int(self.linear_trend(1.0, 0.0, 0, min(500, len(sorted_indices)), 1)[0]))
            seq_id = str(seq_list[sorted_indices[selected_ind]])
            events = self.planner_sequences.query("seq == " + seq_id).values.tolist()
            sorted_indices.pop(selected_ind)
            for event in events:
                all_events.append(event)

        # assign to user
        self.assign_events_to_user(usr, all_events)


    # combine into one method
    def sample_designer(self, usr, type_sequence, starting_range, starting_capacity, starting_cost):

        # capture all events
        all_events = []

        # set user name to view appropriate available vehicles
        self.db_helper.set_user_name(usr)

        # starting seqeunce and new session (just base vehicle), so it is the first session, find event sequnces that start from the base design
        vehicles = self.db_helper.query_vehicles()
        sample_type = "All"
        if type_sequence == 0 and len(vehicles) == 1:
            sample_type = "Start"
        elif type_sequence == 1:
            sample_type = "Open"

        # get preference and requirement information
        # default to no preference and requirements
        pref_type = -1
        range_preference = self.NOPREFERENCE
        capacity_preference = self.NOPREFERENCE
        cost_preference = self.NOPREFERENCE

        # check for preference and requirements
        user_position = self.db_helper.get_user_positions()[usr]
        digital_twin = DigitalTwin.objects.filter(user_position=user_position).first()
        if digital_twin is not None:

            twin_preference = DigitalTwinPreference.objects.filter(Q(digital_twin=digital_twin)&Q(name="range")).first()
            if twin_preference is not None:
                range_preference = twin_preference.pref_value
                pref_type = twin_preference.pref_type # need to check if others are the same

            twin_preference = DigitalTwinPreference.objects.filter(Q(digital_twin=digital_twin)&Q(name="capacity")).first()
            if twin_preference is not None:
                capacity_preference = twin_preference.pref_value
                pref_type = twin_preference.pref_type

            twin_preference = DigitalTwinPreference.objects.filter(Q(digital_twin=digital_twin)&Q(name="cost")).first()
            if twin_preference is not None:
                cost_preference = twin_preference.pref_value
                pref_type = twin_preference.pref_type


        seq_open_distance, seq_first_event_distance, seq_start_and_submit, seq_scores_preferences = self.get_designer_event_scores(sample_type, pref_type, range_preference, capacity_preference, cost_preference,  starting_range, starting_capacity, starting_cost)
        seqs_ids = []
        open_scores = []
        start_scores = []
        all_scores = []
        scores = []
        for seq_id in seq_open_distance:
            seqs_ids.append(seq_id)
            avg_requiement_score = 0
            avg_pref_score = 0
            all_seq_pref_events_scores = seq_scores_preferences[seq_id]
            for seq_pref_event_score in all_seq_pref_events_scores:
                avg_pref_score += seq_pref_event_score/len(all_seq_pref_events_scores)
            open_scores.append(seq_open_distance[seq_id] + avg_pref_score)
            start_scores.append(seq_start_and_submit[seq_id] + avg_pref_score)
            all_scores.append(seq_first_event_distance[seq_id] + avg_pref_score)
            scores.append(avg_pref_score)

        # if there is no preference, the above could be skipped, will modify code later to do this
        is_pref = True
        if (range_preference == self.NOPREFERENCE and
                capacity_preference == self.NOPREFERENCE and
                cost_preference == self.NOPREFERENCE):
            is_pref = False

        all_events = []
        first_event_data = []
        if sample_type == "Open":
            sort_index = numpy.argsort(open_scores)
            if is_pref:
                selected_ind = sort_index[max(0,int(self.linear_trend(1.0, 0.0, 0, min(50, len(sort_index)), 1)[0]))]
            else:
                selected_ind = self.get_random_score_below_max_value(open_scores)
            first_event_data = self.designer_sequences.query("seq == " + str(seqs_ids[selected_ind])).values.tolist()
            for event in first_event_data:
                all_events.append(event)
        if sample_type == "Start":      # currently there are 72 starting and submit designs
            sort_index = numpy.argsort(start_scores)
            if is_pref:
                selected_ind = sort_index[max(0,int(self.linear_trend(1.0, 0.0, 0, min(20, len(sort_index)), 1)[0]))]
            else:
                selected_ind = self.get_random_score_below_max_value(start_scores)
            event_data = self.designer_sequences.query("seq == " + str(seqs_ids[selected_ind])).values.tolist()
            for event in event_data:
                all_events.append(event)
        if sample_type == "All":
            sort_index = numpy.argsort(all_scores)
            if is_pref:
                selected_ind = sort_index[max(0,int(self.linear_trend(1.0, 0.0, 0, min(50, len(sort_index)), 1)[0]))]
            else:
                selected_ind = self.get_random_score_below_max_value(all_scores)
            first_event_data = self.designer_sequences.query("seq == " + str(seqs_ids[selected_ind])).values.tolist()
            for event in first_event_data:
                all_events.append(event)

        while len(all_events) < len(self.team_time_events[usr]):
            sort_index = numpy.argsort(scores)
            if is_pref:
                selected_ind = sort_index[max(0,int(self.linear_trend(1.0, 0.0, 0, min(200, len(sort_index)), 1)[0]))]
            else:
                selected_ind = self.get_random_score_below_max_value(scores)
            event_data = self.designer_sequences.query("seq == " + str(seqs_ids[selected_ind])).values.tolist()
            for event in event_data:
                all_events.append(event)

        # assign events to the user
        self.assign_events_to_user(usr, all_events)

        # open event, return first event to record into the logs
        if len(first_event_data) > 0:
            # seqs, tag, config, range, capacity, cost, velocity]
            return [first_event_data[0][1], first_event_data[0][2], first_event_data[0][3],first_event_data[0][4],first_event_data[0][5],first_event_data[0][6]  ]

    # initial preference mediation methods
    # def sample_design_sequence_preference_design(self, sample_type, pref_type, range_preference, capacity_preference, cost_preference, min_range, max_range, min_capacity, max_capacity, min_cost, max_cost, starting_range, starting_capacity, starting_cost):
    def get_designer_event_scores(self, sample_type, pref_type, range_preference, capacity_preference, cost_preference, starting_range, starting_capacity, starting_cost):

        seq_open_distance = {}
        seq_start_and_submit = {}
        seq_first_event_distance = {}
        seq_scores_preferences = {}
        all_events = self.designer_sequences
        min_values = all_events.min()
        max_values = all_events.max()
        team_events = all_events.values.tolist()
        for team_event in team_events:
            seq_id = str(team_event[0])
            first_event = False
            if seq_id not in seq_open_distance:
                seq_open_distance[seq_id] = 100000000000
                seq_start_and_submit[seq_id] = 100000000000
                seq_first_event_distance[seq_id] = 100000000000
                seq_scores_preferences[seq_id] = []
                first_event = True
            event_type = team_event[2]
            veh_range = team_event[3]
            veh_capacity = team_event[4]
            veh_cost = team_event[5]
            if first_event:
                d = ((((veh_range - starting_range)/(max_values["range"] - min_values["range"]))**2 + \
                    ((veh_capacity - starting_capacity)/(max_values["capacity"] - min_values["capacity"]))**2 + \
                    ((veh_cost - starting_cost)/(max_values["cost"] - min_values["cost"]))**2)**0.5)/1.73
                if event_type == "Open":
                    seq_open_distance[seq_id] = d
                else:
                    seq_open_distance[seq_id] = self.MAXVALUE
                seq_first_event_distance[seq_id] = d

            if event_type == "Submit" and seq_open_distance[seq_id] == self.MAXVALUE:
                seq_start_and_submit[seq_id] = 0

            preference_distance = 0

            if pref_type == 0:
                preference_distance = -(range_preference*veh_range/(max_values["range"] - min_values["range"]) + \
                    capacity_preference*veh_capacity/(max_values["capacity"] - min_values["capacity"]) + \
                    cost_preference*veh_cost/(max_values["cost"] - min_values["cost"]))                                     # smaller norm_distance is better and larger weight sums is better, so negative
            elif pref_type == 1:
                preference_distance = ((((veh_range - range_preference)/(max_values["range"] - min_values["range"]))**2 + \
                    ((veh_capacity - capacity_preference)/(max_values["capacity"] - min_values["capacity"]))**2 + \
                    ((veh_cost - cost_preference)/(max_values["cost"] - min_values["cost"]))**2)**0.5)/1.73

            seq_scores_preferences[seq_id].append(preference_distance)

        return seq_open_distance, seq_first_event_distance, seq_start_and_submit, seq_scores_preferences

    def get_random_score_below_max_value(self, scores):
        ind_to_include = []
        for i, s in enumerate(scores):
            if s < self.MAXVALUE:
                ind_to_include.append(i)
        rnd_index = random.randrange(0, len(ind_to_include))
        return ind_to_include[rnd_index]


# resamples planner event for all users

    def resample_planners_based_on_scenario_and_vehicles(self):
        for usr in self.team_role:
            if self.team_role[usr] == "planner":
                self.sample_planner(usr)

    # get the closest session plan to the target plan metrics
    def get_close_plan(self, usr, profit, startupCost, no_deliveries, business_role):

        # should be already set, but need to make sure
        self.db_helper.set_user_name(usr)

        # initial variables to store and test closest plan
        close_plan = None
        closest_plan_index = -1
        closest_plan_dist = self.MAXVALUE
        min_startup_cost = self.MAXVALUE
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
                d = ((((self.plan_cache[p.id][0] - profit)/max_profit)**2 + ((self.plan_cache[p.id][1] - startupCost)/max_startup_cost)**2 + ((self.plan_cache[p.id][2] - no_deliveries)/max_number_deliveries)**2)**0.5)/1.73
                # add penalty for the fixed cost constraint
                if business_role:
                    if self.plan_cache[p.id][1] > 15000:
                        #d += (self.plan_cache[p.id][1] - 15000)/20000
                        d = self.MAXVALUE
                else:
                    # substract for self bias
                    if str(p.id) in self.self_bias_plans[usr]:
                        d -= self.self_bias[usr]
                dist_scores.append(d)

            # sorted indices by distance
            sorted_indices = numpy.argsort(dist_scores)
            if business_role:
                close_plan = plans[int(sorted_indices[0])]
                # make sure it has some profit
                if self.plan_cache[close_plan.id][1] <= 0:
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
            max_range = -self.MAXVALUE
            max_payload = -self.MAXVALUE
            max_cost = -self.MAXVALUE
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
                closest_dist = self.MAXVALUE
                closest_veh = None
                for v in vehicles:
                    d =  ((((target[0] - v.range)/max_range)**2 + ((target[1] - v.payload)/max_payload)**2 + ((target[2] - v.cost)/max_cost)**2)**0.5)/1.73

                    # subtract self-bias
                    if str(v.id) in self.self_bias_designs[usr]:
                        d -= self.self_bias[usr]

                    # bias off base design
                    if v.config == '*aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3' and bias_from_base_design:
                        d += 2

                    # if closest
                    if d < closest_dist:
                        closest_dist = d
                        closest_veh = v

                used_vehicles.append(closest_veh)

        return used_vehicles, closest_dist

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
                twin_info_message(self.session.id, "error : ++++++++++++++++++++++ invalid action queue ++++++++++++++++++++++ ")
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
            user_pos = UserPosition.objects.create(position=structurePositions[x], user=teamUsers[x], session=newSession)

        warehouseAddress = Address.objects.filter(region="warehouse").first()
        warehouseGroup = Group.objects.filter(name="All", structure=sessionStructure).first()
        Warehouse.objects.create(address=warehouseAddress, group=warehouseGroup, session=newSession)

        baseConfig = "*aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3"
        Vehicle.objects.create(tag="base", config=baseConfig, result="Success", range=10.0, velocity=20.0, cost=3470.20043945312, payload=5, group=warehouseGroup, session=newSession)

        # initialize preference objects
        self.init_session_preference(newSession)

        twin_info_message(newSession.id, 'session_created_id')

        return newSession

    def init_session_preference(self, session):

        # get database helper and user roles
        db_helper = DatabaseHelper(session)
        user_positions = db_helper.get_user_positions()

        digital_twin_setups = []

        # for each user, and database objects
        for user_pos in user_positions:

            # if no object already
            digital_twin_user_position_query = DigitalTwin.objects.filter(user_position=user_positions[user_pos])

            if len(digital_twin_user_position_query) == 0:
                # objects to store preferences
                digital_twin_user_setup = DigitalTwin.objects.create(user_position=user_positions[user_pos])
                digital_twin_setups.append(digital_twin_user_setup)
                pref_vars = []
                if user_positions[user_pos].position.role.name == "Business" or "Planner" in user_positions[user_pos].position.role.name :
                    pref_vars = ["profit", "fixed_cost", "no_customers"]
                else:
                    pref_vars = ["range", "capacity", "cost"]
                for var_name in pref_vars:
                    new_preference_setup = DigitalTwinPreference.objects.create(digital_twin=digital_twin_user_setup)
                    new_preference_setup.name = var_name
                    new_preference_setup.pref_value = 0
                    new_preference_setup.save()

            else:
                digital_twin_setups.append(digital_twin_user_position_query.first())

        return digital_twin_setups

    def preference_example(self):

        prefs = {'channel' : 'twin',
            'type' : 'twin.pref',
            'session_id' : self.session.id,
            'prefs' : [
                {

                    'user_id' : 'arl_1',
                    'pref_type' : 1,        # 0 weight sums, 1 target or goal based, for now use 0
                    'profit' : 9000,
                    'fixed_cost' : 15000,
                    'no_customers' : 36
                },
                {
                    'user_id' : 'arl_2',
                    'pref_type' : 1,        # 0 weight sums, 1 target or goal based, for now use 0
                    'range' : self.NOPREFERENCE,
                    'capacity' : self.NOPREFERENCE,
                    'cost' : self.NOPREFERENCE
                },
                {
                    'user_id' : 'arl_3',
                    'pref_type' : 1,        # 0 weight sums, 1 target or goal based, for now use 0
                    'range' : self.NOPREFERENCE,
                    'capacity' : self.NOPREFERENCE,
                    'cost' : self.NOPREFERENCE
                },
                {
                    'user_id' : 'arl_4',
                    'pref_type' : 1,        # 0 weight sums, 1 target or goal based, for now use 0
                    'profit' : 9000,
                    'fixed_cost' : 15000,
                    'no_customers' : 36
                },
                {
                    'user_id' : 'arl_5',
                    'pref_type' : 1,        # 0 weight sums, 1 target or goal based, for now use 0
                    'profit' : 9000,
                    'fixed_cost' : 15000,
                    'no_customers' : 36
                },
                {
                    'user_id' : 'arl_6',
                    'pref_type' : 1,        # 0 weight sums, 1 target or goal based, for now use 0
                    'profit' : 9000,
                    'fixed_cost' : 15000,
                    'no_customers' : 36
                }
            ],
        }

        return json.dumps(prefs)


    def set_preference(self, session, pref_info):

        self.init_session_preference(session)
        msg = ""
        user_id = ""
        try:

            # get database helper and user roles
            self.db_helper = DatabaseHelper(session)
            user_roles = self.db_helper.get_user_roles()
            user_positions = self.db_helper.get_user_positions()

            preference_dict = json.loads(pref_info)
            session_id = preference_dict['session_id']
            prefs = preference_dict['prefs']
            print("received len ", len(prefs))
            for pref in prefs:
                user_id = pref['user_id']
                if user_id in user_roles and user_id in user_positions:
                    digital_twin = DigitalTwin.objects.filter(user_position=user_positions[user_id]).first()
                    role_metrics = []
                    if 'Business' in user_roles[user_id] or 'Plan' in user_roles[user_id]:
                        role_metrics = ['profit', 'fixed_cost', 'no_customers']
                    elif 'Design' in user_roles[user_id]:
                        role_metrics = ['range', 'capacity', 'cost']
                    for var_name in role_metrics:
                        twin_preference = DigitalTwinPreference.objects.filter(Q(digital_twin=digital_twin)&Q(name=var_name)).first()
                        twin_preference.pref_value = pref[var_name]
                        twin_preference.pref_type = pref['pref_type']
                        twin_preference.save()
                        print("set_pref", user_id, var_name, pref[var_name])
                    twin_info_message(session.id, "added preference for " + user_id)
                else:
                    raise Exception("user id invalid")

            twin_pref_message(session.id, 'preference_set')

        except Exception as e:
            traceback.print_exc()
            twin_pref_message(session.id, json.dumps({
                'preference_error' : str(e),
                'user_id' : user_id
            }))

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

    # export to export session data to data logs
    def export_log_data_for_visualization(self):
        with open("designer.txt", "a") as myfile:
            for lgdata in self.designer_vis_log:
                myfile.write(lgdata)
            myfile.close()
        with open("planner.txt", "a") as myfile:
            for lgdata in self.plan_vis_log:
                myfile.write(lgdata)
            myfile.close()
        with open("business.txt", "a") as myfile:
            for lgdata in self.business_vis_log:
                myfile.write(lgdata)
            myfile.close()
