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

from exper.models import DigitalTwin, DigitalTwinPreference, DigitalTwinRequirement
from api.messaging import twin_info_message, twin_pref_message, twin_complete_message, twin_uncertainty_message


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

        self.business_variables = ["profit", "cost", "no_customers", "total_weight", "parcel_weight", "food_weight", "number_parcel", "number_food", "number_food_and_parcel"]
        self.planner_variables = ["profit", "cost", "no_customers", "weight_delivered", "parcel_delivered", "food_delivered", "number_parcel", "number_food"]
        self.designer_variables = ["range", "capacity", "cost", "no_structures", "no_motors", "no_foils", "no_components"]

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
        self.team_role['session'] = "session"   # a dummy role to add experimental commands
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
        #self.set_uncertainties(session, self.uncertainty_example())

        # sample initial events
        self.generate_initial_events()


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

            if usr == "session":
                self.resample_planners_based_on_scenario_and_vehicles()

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
                        self.cache_business_metrics(t, usr, "Scenario", number_selected, 0, 0, scenario_str)

                    else:
                        self.cache_business_metrics(t, usr, "Scenario", 56, 0, 0, "")
                        print("default scenario submit")
                        twin_info_message(self.session.id, "default scenario submit")
                    self.business_scenario_submitted = True

                # open plan , gets all current available team plans and selects a plan with the close metrics
                if action_info[0] == "Open":
                    close_plan, clos_dist = self.get_close_plan(usr, float(action_info[1]),float(action_info[2]),float(action_info[3]), False)
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
                    closest_plan, clos_dist = self.get_close_plan(usr, float(action_info[1]), float(action_info[2]), float(action_info[3]), True)
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
                    close_plan, clos_dist = self.get_close_plan(usr, profit, startupCost, no_deliveries, False)
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
                                            scenario_customer = CustomerScenario.objects.filter(Q(customer=customer_cp['id'])&Q(scenario=scenario_obj['id'])).first()
                                            # get distance from warehouse to first customer , or from the previous customer
                                            if ii == 0:
                                                current_range += ((float(customer_cp['address']['x']) - float(scenario_obj['warehouse']['address']['x']))**2 + (float(customer_cp['address']['z']) - float(scenario_obj['warehouse']['address']['z']))**2)**0.5
                                            else:
                                                current_range += ((float(customer_cp['address']['x']) - float(last_customer['address']['x']))**2 + (float(customer_cp['address']['z']) - float(last_customer['address']['z']))**2)**0.5
                                            current_capacity += customer['weight'] + scenario_customer.deviation
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


    def planner_agent_calc(self, usr, action_str):

        self.db_helper.set_user_name(usr)

        # create the plan input string with empty paths, where each path has a closest vehicle as recommended by the planner AI
        plan = {}
        plan['paths'] = []
        scenario_obj = self.db_helper.get_scenario()

        # since we the planner is the adapter and the plan metrics are high, assist in meeting cost constraint
        fixed_cost = 0

        # get the vehicle metrics for each path and add a closest team vehicle and add an empty plan
        deliveries = action_str.split('_')[1].split("Path")
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
                    plan["paths"].append(path_obj)

                    fixed_cost += used_vehicle.cost

                except Exception as e:
                    print(e)
                    twin_info_message(self.session.id, str(e))

        # add an empty path to the plan
        plan['scenario'] = scenario_obj

        # convert to string for the planner AI
        json_str = json.dumps(plan)

        # use planner agent to create new plan
        o = OpsPlan(json_str)
        plan_ai_json = o.output.replace("\'","\"").replace("True", "true").replace("False", "false")

        # save the plan json object
        json_obj_plan = json.loads(plan_ai_json)

        # set tag
        json_obj_plan['tag'] = "ai_" + usr

        # convert the json plan to a string to save to a dataLog and calculate metrics
        plan_str = self.convert_plan_json_to_str(json_obj_plan)

        # get the metrics of the new plan
        result = OpsService(plan_str)
        result_dict = {}
        result_dict['profit'] = result.profit
        result_dict['cost'] = result.startupCost
        result_dict['no_customers'] = result.number_deliveries
        result_dict['weight_delivered'] = result.total_weight_delivered
        result_dict['parcel_delivered'] = result.total_parcel_delivered
        result_dict['food_delivered'] = result.total_food_delivered
        result_dict['number_parcel'] = result.number_parcel_deliveries
        result_dict['number_food'] = result.number_food_deliveries
        return result_dict

    def planner_manual_calc(self, usr, action_str):


        self.db_helper.set_user_name(usr)

        # reset plan, since the manual event includes all path information
        # for all vehicles in the plan
        plan = {}
        plan['paths'] = []
        scenario_obj = self.db_helper.get_scenario()
        plan['scenario'] = scenario_obj

        # add variable for fixed cost
        fixed_cost = 0

        # get path tokens
        add_path_tokens = action_str.split('_')[1].split(";")
        current_path = None
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
                plan["paths"].append(path_obj)
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
                                scenario_customer = CustomerScenario.objects.filter(Q(customer=customer_cp['id'])&Q(scenario=scenario_obj['id'])).first()
                                # get distance from warehouse to first customer , or from the previous customer
                                if ii == 0:
                                    current_range += ((float(customer_cp['address']['x']) - float(scenario_obj['warehouse']['address']['x']))**2 + (float(customer_cp['address']['z']) - float(scenario_obj['warehouse']['address']['z']))**2)**0.5
                                else:
                                    current_range += ((float(customer_cp['address']['x']) - float(last_customer['address']['x']))**2 + (float(customer_cp['address']['z']) - float(last_customer['address']['z']))**2)**0.5
                                current_capacity += customer['weight'] + scenario_customer.deviation
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


        # convert the json plan to a string to save to a DataLog and calculate metrics
        plan_str = self.convert_plan_json_to_str(plan)
        #print(plan_str)
        result = OpsService(plan_str)
        result_dict = {}
        result_dict['profit'] = result.profit
        result_dict['cost'] = result.startupCost
        result_dict['no_customers'] = result.number_deliveries
        result_dict['weight_delivered'] = result.total_weight_delivered
        result_dict['parcel_delivered'] = result.total_parcel_delivered
        result_dict['food_delivered'] = result.total_food_delivered
        result_dict['number_parcel'] = result.number_parcel_deliveries
        result_dict['number_food'] = result.number_food_deliveries
        return result_dict

    def sample_business(self, usr):


        self.db_helper.set_user_name(usr)
        scenairo = self.db_helper.get_scenario()

        # get preference and requirement information
        # default to no preference and requirements
        pref_type = -1
        pref_values = {}
        req_values = {}

        # check for preference and requirements
        user_position = self.db_helper.get_user_positions()[usr]
        digital_twin = DigitalTwin.objects.filter(user_position=user_position).first()
        is_pref = False
        if digital_twin is not None:

            for var_name in self.business_variables:

                twin_preference = DigitalTwinPreference.objects.filter(Q(digital_twin=digital_twin)&Q(name=var_name)).first()
                if twin_preference is not None:
                    pref_values[var_name] = twin_preference.pref_value
                    if twin_preference.pref_value != self.NOPREFERENCE:
                        is_pref = True
                        pref_type = twin_preference.pref_type # need to check if others are the same

                twin_requirement = DigitalTwinRequirement.objects.filter(Q(digital_twin=digital_twin)&Q(name=var_name)).first()
                if twin_requirement is not None:
                    req_values[var_name] = [twin_requirement.lower_limit, twin_requirement.upper_limit]
                    if twin_requirement.lower_limit != self.MINVALUE or twin_requirement.upper_limit != self.MAXVALUE:
                        is_pref = True


        scenario_metrics = {}
        select_metrics = {}
        all_events = self.business_sequences.drop_duplicates(subset=['seq'], keep='last').values.tolist()
        for event in all_events:
            if "Selected" in event[1]:
                metrics = event[1].split(';')
                select_metrics[event[0]] = { 'profit' : float(metrics[1]) , 'cost' : float(metrics[2]), 'no_customers' : float(metrics[3]) }
        all_events = self.business_sequences.drop_duplicates(subset=['seq'], keep='first').values.tolist()
        for event in all_events:
            if "Scenario" in event[1]:
                metrics = event[1].split(';')[1].split("|")
                scenario_metrics[event[0]] = metrics

        # for now, get business sequences that submit a scenario for the first event and selected final plan as the last event
        intersection = scenario_metrics.keys() & select_metrics.keys()
        scenario_calculations = {}
        for key in intersection:
            used_locations = []
            scenario_calculations[key] = {"number_food_and_parcel" : 0, "number_parcel" : 0, "number_food" : 0, "parcel_weight" : 0, "food_weight" : 0, "total_weight" : 0}
            for location in scenario_metrics[key]:
                loc = location.split(":")
                if len(loc) == 2:

                    suggested_x = float(loc[0])
                    suggested_z = float(loc[1])

                    closest_dist = self.MAXVALUE
                    closest_location = None
                    closest_customer = None
                    # for each customer in the selected business scenario, get its proximity to the suggestion and if it is feasible and not already included
                    for customer in scenairo['customers']:

                        customer_x = float(customer['address']['x'])
                        customer_z = float(customer['address']['z'])

                        d = ((suggested_x - customer_x)**2 + (suggested_z - customer_z)**2)**0.5

                        if d < closest_dist and location not in used_locations:
                            closest_dist = d
                            closest_location = location
                            closest_customer = customer

                    scenario_customer = CustomerScenario.objects.filter(Q(customer=closest_customer['id'])&Q(scenario=scenairo['id'])).first()
                    if closest_customer is not None:
                        used_locations.append(closest_location)
                        scenario_calculations[key]['number_food_and_parcel'] = scenario_calculations[key]['number_food_and_parcel'] + 1
                        scenario_calculations[key]['total_weight'] = scenario_calculations[key]['total_weight'] + scenario_customer.deviation
                        if "food" in closest_customer['payload']:
                            scenario_calculations[key]['number_food'] = scenario_calculations[key]['number_food'] + 1
                            scenario_calculations[key]['food_weight'] = scenario_calculations[key]['food_weight'] + closest_customer['weight'] + scenario_customer.deviation
                        else:
                            scenario_calculations[key]['number_parcel'] = scenario_calculations[key]['number_parcel'] + 1
                            scenario_calculations[key]['parcel_weight'] = scenario_calculations[key]['parcel_weight'] + closest_customer['weight'] + scenario_customer.deviation


        max_values = {}
        max_values['profit'] = self.MINVALUE
        max_values['cost'] = self.MINVALUE
        max_values['no_customers'] = self.MINVALUE
        max_values['total_weight'] = self.MINVALUE
        max_values['parcel_weight'] = self.MINVALUE
        max_values['food_weight'] = self.MINVALUE
        max_values['number_parcel'] = self.MINVALUE
        max_values['number_food'] = self.MINVALUE
        max_values['number_food_and_parcel'] = self.MINVALUE

        for key in intersection:
            max_values['profit'] = max(select_metrics[key]['profit'], max_values['profit'])
            max_values['cost'] = max(select_metrics[key]['cost'], max_values['cost'])
            max_values['no_customers'] = max(select_metrics[key]['no_customers'], max_values['no_customers'])
            max_values['total_weight'] = max(scenario_calculations[key]['total_weight'], max_values['total_weight'])
            max_values['parcel_weight'] = max(scenario_calculations[key]['parcel_weight'], max_values['parcel_weight'])
            max_values['food_weight'] = max(scenario_calculations[key]['food_weight'], max_values['food_weight'])
            max_values['number_parcel'] = max(scenario_calculations[key]['number_parcel'], max_values['number_parcel'])
            max_values['number_food'] = max(scenario_calculations[key]['number_food'], max_values['number_food'])
            max_values['number_food_and_parcel'] = max(scenario_calculations[key]['number_food_and_parcel'], max_values['number_food_and_parcel'])


        results = {}
        feasible = 0

        for key in intersection:
            results[key] = 0

        for key in intersection:
            values = {'profit' : select_metrics[key]['profit'], 'cost' : select_metrics[key]['cost'], 'no_customers' : select_metrics[key]['no_customers'],
                'total_weight' : scenario_calculations[key]['total_weight'], 'parcel_weight' : scenario_calculations[key]['parcel_weight'], 'food_weight' : scenario_calculations[key]['food_weight'],
                'number_parcel' : scenario_calculations[key]['number_parcel'], 'number_food' : scenario_calculations[key]['number_food'], 'number_food_and_parcel' : scenario_calculations[key]['number_food_and_parcel'] }
            p = 0
            has_constraint = False
            for req in req_values:
                if req_values[req][0] != self.MINVALUE and req_values[req][1] != self.MAXVALUE:
                    has_constraint = True
                    p += self.constraint_penalty(values[req], req_values[req][0],  req_values[req][1], max_values[req])
            if p == 0 and has_constraint: # big reward for feasible design
                p = -10
                feasible += 1
            results[key] = results[key] + p

        weighted_sum_preferences = {}
        for key in intersection:

            preference_distance = 0
            scaling_factor = 0

            values = {'profit' : select_metrics[key]['profit'], 'cost' : select_metrics[key]['cost'], 'no_customers' : select_metrics[key]['no_customers'],
                'total_weight' : scenario_calculations[key]['total_weight'], 'parcel_weight' : scenario_calculations[key]['parcel_weight'], 'food_weight' : scenario_calculations[key]['food_weight'],
                'number_parcel' : scenario_calculations[key]['number_parcel'], 'number_food' : scenario_calculations[key]['number_food'] , "number_food_and_parcel" : scenario_calculations[key]['number_food_and_parcel'] }
            for var_name in pref_values:
                if pref_type == 0 and pref_values[var_name] != self.NOPREFERENCE:
                    preference_distance += -pref_values[var_name]*values[var_name]/max_values[var_name]                # assumeweights are normalized to 1
                    scaling_factor = 1
                elif pref_type == 1 and pref_values[var_name] != self.NOPREFERENCE:                                   # smaller norm_distance is better and larger weight sums is better, so negative
                    preference_distance += ((values[var_name] - pref_values[var_name])/max(max_values[var_name], pref_values[var_name]))**2
                    scaling_factor += 1
            if pref_type == 1:
                results[key] = results[key] + (-0.25 + (preference_distance**0.5)/(max(scaling_factor,1)**0.5))            # same as designer -0.25 for good close events and 0.75 for further away
            else:
                weighted_sum_preferences[key] = preference_distance


        # weighted sums preference calculations to scale to around -0.25 to 0.75 (from top to bottom)
        if pref_type == 0:
            min_pref = self.MAXVALUE
            max_pref = self.MINVALUE
            for key in weighted_sum_preferences:
                min_pref = min(weighted_sum_preferences[key], min_pref)
                max_pref = max(weighted_sum_preferences[key], max_pref)
            for key in weighted_sum_preferences:
                results[key] = results[key] + (-0.25 + (weighted_sum_preferences[key] - min_pref)/max((max_pref - min_pref), 1))

        # get sample size
        MM = feasible
        # get top 5 ranked at most
        MM = min(MM, 5)

        sorted_results = {k: v for k, v in sorted(results.items(), key=lambda item: item[1])}

        # selected index
        selected_ind = int(self.linear_trend(1.0, -1.0, 0, MM, 1)[0])
        seq_id = list(sorted_results.keys())[selected_ind]
        seq_events = self.business_sequences.query("seq == " + str(seq_id)).values.tolist()

        # assign timestamps to each event
        business_time_events = self.linear_trend(0.32, 0.68, 0, 20, len(seq_events))
        business_time_events.sort()

        # make the last selected event at 20 min
        business_time_events[len(business_time_events) - 1] = 20

        # set the last submit scenario to the first event
        self.team_role[usr] = "business"
        self.team_data[usr] = None
        self.team_time_events[usr] = business_time_events

        # assign event to the user
        self.assign_events_to_user(usr, seq_events)


    def sample_planner(self, usr, starting_event):

        self.db_helper.set_user_name(usr)

        # get preference and requirement information
        # default to no preference and requirements
        pref_type = -1
        pref_values = {}
        req_values = {}
        for var_name in self.planner_variables:
            pref_values[var_name] = self.NOPREFERENCE
            req_values[var_name] = [self.MINVALUE, self.MAXVALUE]

        # check for preference and requirements
        user_position = self.db_helper.get_user_positions()[usr]
        digital_twin = DigitalTwin.objects.filter(user_position=user_position).first()
        is_pref = False
        if digital_twin is not None:

            for var_name in self.planner_variables:

                twin_preference = DigitalTwinPreference.objects.filter(Q(digital_twin=digital_twin)&Q(name=var_name)).first()
                if twin_preference is not None:
                    pref_values[var_name] = twin_preference.pref_value
                    if twin_preference.pref_value != self.NOPREFERENCE:
                        is_pref = True
                        pref_type = twin_preference.pref_type # need to check if others are the same

                twin_requirement = DigitalTwinRequirement.objects.filter(Q(digital_twin=digital_twin)&Q(name=var_name)).first()
                if twin_requirement is not None:
                    req_values[var_name] = [twin_requirement.lower_limit, twin_requirement.upper_limit]
                    if twin_requirement.lower_limit != self.MINVALUE or twin_requirement.upper_limit != self.MAXVALUE:
                        is_pref = True

        starting_submit_ids = []
        open_distance = {}
        submits_ids = []
        all_seqs = []
        starting_seqs = {}
        planner_db = self.planner_sequences.values.tolist()
        for i, planner_event in enumerate(planner_db):
            try:
                if planner_event[0] not in starting_seqs:
                    start_seq =  "Start" in planner_event[1]
                    starting_seqs[planner_event[0]] = start_seq
                    open_distance[planner_event[0]] = 0
                    if not start_seq:
                        metrics = planner_event[1].split("=")[1].split(",")
                        if len(metrics) == 3:
                            close_plan, clos_dist = self.get_close_plan(usr, float(metrics[0]), float(metrics[1]), float(metrics[2]), False)
                            open_distance[planner_event[0]] = clos_dist # penalize far away starting plans


                if "Submit" in planner_event[1]:
                    if "Manual" in planner_db[i - 1][1]:
                        submits_ids.append(i)
                        if starting_seqs[planner_event[0]] or open_distance[planner_event[0]] < 0.05:
                            starting_submit_ids.append(i)
                            all_seqs.append(planner_event[0])
                    elif "Agent" in planner_db[i - 1][1]:
                        submits_ids.append(i)
                        if starting_seqs[planner_event[0]] or open_distance[planner_event[0]] < 0.05:
                            starting_submit_ids.append(i)
                            all_seqs.append(planner_event[0])
            except Exception as e:
                traceback.print_exc()
                pass

        if is_pref:

            MM = 40
            seq_results = {}
            print("calculating planner agent with preference ...")
            for i in range(MM):
            #for i in range(len(submits_ids)):
                try:
                    idx = starting_submit_ids[random.randrange(0, len(starting_submit_ids))]
                    #idx = submits_ids[i]
                    if "Manual" in planner_db[idx - 1][1]:
                        results = self.planner_manual_calc(usr, planner_db[idx - 1][1])
                        seq_results[planner_db[idx - 1][0]] = results
                    elif "Agent" in planner_db[idx - 1][1]:
                        results = self.planner_agent_calc(usr, planner_db[idx - 1][1])
                        seq_results[planner_db[idx - 1][0]] = results
                except Exception as e:
                    traceback.print_exc()
                    pass

            print("done calculating planner ...")

            #  profit, startupCost, number_deliveries, total_weight_delivered, total_parcel_delivered, total_food_delivered, number_parcel_deliveries, number_food_deliveries
            max_values_dict = {}
            max_values_dict['profit'] = 0.01
            max_values_dict['cost'] = 0.01
            max_values_dict['no_customers'] = 0.01
            max_values_dict['weight_delivered'] = 0.01
            max_values_dict['parcel_delivered'] = 0.01
            max_values_dict['food_delivered'] = 0.01
            max_values_dict['number_parcel'] = 0.01
            max_values_dict['number_food'] = 0.01
            results = {}
            for seq in seq_results:
                max_values_dict['profit'] = max(max_values_dict['profit'], seq_results[seq]['profit'])
                max_values_dict['cost'] = max(max_values_dict['cost'], seq_results[seq]['cost'])
                max_values_dict['no_customers'] = max(max_values_dict['no_customers'], seq_results[seq]['no_customers'])
                max_values_dict['weight_delivered'] = max(max_values_dict['weight_delivered'], seq_results[seq]['weight_delivered'])
                max_values_dict['parcel_delivered'] = max(max_values_dict['parcel_delivered'], seq_results[seq]['parcel_delivered'])
                max_values_dict['food_delivered'] = max(max_values_dict['food_delivered'], seq_results[seq]['food_delivered'])
                max_values_dict['number_parcel'] = max(max_values_dict['number_parcel'], seq_results[seq]['number_parcel'])
                max_values_dict['number_food']  = max(max_values_dict['number_food'], seq_results[seq]['number_food'])
                results[seq] = 0

            feasible = 0
            has_constraints = False
            for seq in seq_results:
                p = 0
                has_constraint = False
                for req in req_values:
                    if req_values[req][0] != self.MINVALUE and req_values[req][1] != self.MAXVALUE:
                        has_constraints = True
                        has_constraint = True
                        p += self.constraint_penalty(seq_results[seq][req], req_values[req][0],  req_values[req][1], max_values_dict[req])
                if p == 0 and has_constraint: # big reward for feasible design
                    p = -10
                    feasible += 1
                results[seq] += p


            # get cloesst to feasible
            if feasible == 0 and has_constraints:
                feasible = MM/10                            # get closest feasible
            elif not has_constraints:
                feasible = MM/10

            weighted_sum_preferences = {}
            for seq in seq_results:
                preference_distance = 0
                scaling_factor = 0
                for var_name in pref_values:
                    if pref_type == 0 and pref_values[var_name] != self.NOPREFERENCE:
                        preference_distance += -pref_values[var_name]*seq_results[seq][var_name]/max_values_dict[var_name]                # assumeweights are normalized to 1
                        scaling_factor = 1
                    elif pref_type == 1 and pref_values[var_name] != self.NOPREFERENCE:                                           # smaller norm_distance is better and larger weight sums is better, so negative
                        preference_distance += ((seq_results[seq][var_name] - pref_values[var_name])/max(max_values_dict[var_name],pref_values[var_name]))**2
                        scaling_factor += 1

                if pref_type == 1:
                    results[seq]  = results[seq]  + (-0.25 + (preference_distance**0.5)/(max(scaling_factor,1)**0.5))            # same as designer -0.25 for good close events and 0.75 for further away, try and reward top portion
                else:
                    weighted_sum_preferences[seq] = preference_distance

            # weighted sums preference calculations to scale to around -0.25 to 0.75 (from top to bottom)
            if pref_type == 0:
                min_pref = self.MAXVALUE
                max_pref = self.MINVALUE
                for seq in weighted_sum_preferences:
                    min_pref = min(weighted_sum_preferences[seq], min_pref)
                    max_pref = max(weighted_sum_preferences[seq], max_pref)
                for seq in weighted_sum_preferences:
                    results[seq] = results[seq] + (-0.25 + (weighted_sum_preferences[seq] - min_pref)/max((max_pref - min_pref), 1))

            print(usr, results)

            sorted_results = {k: v for k, v in sorted(results.items(), key=lambda item: item[1])}
            selected_ind = int(self.linear_trend(1.0, -1.0, 0, feasible, 1)[0])

            # sample new events
            all_events = []

            # fill up user events with sequences bias by score
            while len(all_events) < len(self.team_time_events[usr]):
                list_seq_ids = list(sorted_results.keys())
                selected_ind = int(self.linear_trend(1.0, -1.0, 0, min(len(list_seq_ids), feasible), 1)[0])
                seq_id = list_seq_ids[selected_ind]
                events = self.planner_sequences.query("seq == " + str(seq_id)).values.tolist()
                sorted_results.pop(seq_id)
                for event in events:
                    all_events.append(event)

            # assign to user
            self.assign_events_to_user(usr, all_events)

        else:

            all_events = []
            # fill up user events with sequences bias by score
            while len(all_events) < len(self.team_time_events[usr]):
                seq_ind = random.randrange(0, len(all_seqs))
                seq_id = all_seqs[seq_ind]
                events = self.planner_sequences.query("seq == " + str(seq_id)).values.tolist()
                all_seqs.pop(seq_ind)
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
        # All ; open ort staring sequence near the base design
        sample_type = "All"
        # 0 and first experimental session, starting sequence
        if type_sequence == 0 and len(vehicles) == 1:
            sample_type = "Start"
        elif type_sequence == 1:        # sequnce with an open
            sample_type = "Open"

        # get preference and requirement information
        # default to no preference and requirements
        pref_type = -1
        pref_values = {}
        req_values = {}
        for var_name in self.designer_variables:
            pref_values[var_name] = self.NOPREFERENCE
            req_values[var_name] = [self.MINVALUE, self.MAXVALUE]

        # check for preference and requirements
        user_position = self.db_helper.get_user_positions()[usr]
        digital_twin = DigitalTwin.objects.filter(user_position=user_position).first()
        is_pref = False
        if digital_twin is not None:

            for var_name in self.designer_variables:

                twin_preference = DigitalTwinPreference.objects.filter(Q(digital_twin=digital_twin)&Q(name=var_name)).first()
                if twin_preference is not None:
                    pref_values[var_name] = twin_preference.pref_value
                    if twin_preference.pref_value != self.NOPREFERENCE:
                        is_pref = True
                        pref_type = twin_preference.pref_type # need to check if others are the same

                twin_requirement = DigitalTwinRequirement.objects.filter(Q(digital_twin=digital_twin)&Q(name=var_name)).first()
                if twin_requirement is not None:
                    req_values[var_name] = [twin_requirement.lower_limit, twin_requirement.upper_limit]
                    if twin_requirement.lower_limit != self.MINVALUE or twin_requirement.upper_limit != self.MAXVALUE:
                        is_pref = True


        # get score of designer events
        # score for open distance, distance from first event, if the sequence is a satring sequence with a submit,
        # preference scores based on design submits, requirement scores based on design submits
        seq_open_distance, seq_first_event_distance, seq_start_and_submit, seq_scores_preferences, seq_scores_requirements = self.get_designer_event_scores(usr, sample_type, pref_type, pref_values, req_values, starting_range, starting_capacity, starting_cost)

        seqs_ids = []           # all sequence ids
        open_scores = []        # all open sequences ids
        start_scores = []       # all starting sequence scores
        all_scores = []         # all scores
        scores = []

        MM_open = 0
        MM_start = 0
        MM_all = 0
        MM_scores = 50

        # infeasible sequences have values around 10
        # ok sequences have values around 0 - -1
        # feasible submits sequences have values around -10
        for seq_id in seq_open_distance:
            seqs_ids.append(seq_id)

            # get average preference score
            avg_pref_score = 0
            all_seq_pref_events_scores = seq_scores_preferences[seq_id]
            for seq_pref_event_score in all_seq_pref_events_scores:
                avg_pref_score += seq_pref_event_score/len(all_seq_pref_events_scores)

            # get requirement scores, reward feasible sequences and penalized infeasible
            avg_req_score = 0
            all_req_events_scores = seq_scores_requirements[seq_id]
            for seq_req_event_score in all_req_events_scores:
                avg_req_score += seq_req_event_score/len(all_req_events_scores)

            open_score = seq_open_distance[seq_id] + avg_pref_score + avg_req_score
            if seq_open_distance[seq_id] < self.MAXVALUE:
                MM_open += 1
            open_scores.append(open_score)

            start_score = seq_start_and_submit[seq_id] + avg_pref_score + avg_req_score
            if start_score < self.MAXVALUE:
                MM_start += 1
            start_scores.append(start_score)

            all_score = seq_first_event_distance[seq_id] + avg_pref_score + avg_req_score
            if all_score < self.MAXVALUE:
                MM_all += 1
            all_scores.append(all_score)

            scores.append(avg_pref_score + avg_req_score)


        all_events = []
        first_event_data = []

        # task 1 and task 2 preferences and actions constraints
        if is_pref:

            if sample_type == "Open":
                sort_index = numpy.argsort(open_scores)
                MM_open = min(MM_open, 20)
                MM_open = max(MM_open, 4)
                selected_ind = sort_index[max(0,int(self.linear_trend(1.0, -1.0, 0, MM_open, 1)[0]))]
                first_event_data = self.designer_sequences.query("seq == " + str(seqs_ids[selected_ind])).values.tolist()
                for event in first_event_data:
                    all_events.append(event)

            if sample_type == "Start":      # currently there are 72 starting and submit designs
                sort_index = numpy.argsort(start_scores)
                MM_start = min(MM_start, 20)
                MM_start = max(MM_start, 4)
                selected_ind = sort_index[max(0,int(self.linear_trend(1.0, -1.0, 0, MM_start, 1)[0]))]
                first_event_data = self.designer_sequences.query("seq == " + str(seqs_ids[selected_ind])).values.tolist()
                for event in first_event_data:
                    all_events.append(event)

            if sample_type == "All":
                sort_index = numpy.argsort(all_scores)
                MM_all = min(MM_all, 20)
                MM_all = max(MM_all, 4)
                selected_ind = sort_index[max(0,int(self.linear_trend(1.0, -1.0, 0, MM_all, 1)[0]))]
                first_event_data = self.designer_sequences.query("seq == " + str(seqs_ids[selected_ind])).values.tolist()
                for event in first_event_data:
                    all_events.append(event)

            while len(all_events) < len(self.team_time_events[usr]):
                sort_index = numpy.argsort(scores)
                selected_ind = sort_index[max(0,int(self.linear_trend(1.0, -1.0, 0, max(MM_scores, 1), 1)[0]))]
                event_data = self.designer_sequences.query("seq == " + str(seqs_ids[selected_ind])).values.tolist()
                for event in event_data:
                    all_events.append(event)

        else:       # pseudo legacy code, but changed a bit to be a little cleaner

            # get the first event sequence
            selected_ind = -1
            if sample_type == "Open":
                selected_ind = self.get_random_score_below_max_value(open_scores)
            if sample_type == "Start":
                selected_ind = self.get_random_score_below_max_value(start_scores)
            if sample_type == "All":
                selected_ind = self.get_random_score_below_max_value(all_scores)

            first_event_data = self.designer_sequences.query("seq == " + str(seqs_ids[selected_ind])).values.tolist()
            for event in first_event_data:
                all_events.append(event)

            # add remaining events
            while len(all_events) < len(self.team_time_events[usr]):
                sort_index = numpy.argsort(scores)
                selected_ind = self.get_random_score_below_max_value(scores)
                event_data = self.designer_sequences.query("seq == " + str(seqs_ids[selected_ind])).values.tolist()
                for event in event_data:
                    all_events.append(event)

        # assign events to the user
        self.assign_events_to_user(usr, all_events)

        # open event, return first event to record into the logs
        if len(first_event_data) > 0:
            # seqs, tag, config, range, capacity, cost, velocity], need to return a cleaner dictionary
            return [first_event_data[0][1], first_event_data[0][2], first_event_data[0][3],first_event_data[0][4],first_event_data[0][5],first_event_data[0][6]  ]


    # initial preference mediation methods
    # def sample_design_sequence_preference_design(self, sample_type, pref_type, range_preference, capacity_preference, cost_preference, min_range, max_range, min_capacity, max_capacity, min_cost, max_cost, starting_range, starting_capacity, starting_cost):
    def get_designer_event_scores(self, usr, sample_type, pref_type, pref_values, req_values, starting_range, starting_capacity, starting_cost):

        seq_open_distance = {}
        seq_start_and_submit = {}
        seq_first_event_distance = {}
        seq_scores_preferences = {}
        seq_scores_requirements = {}
        seq_first_event_type = {}
        all_events = self.designer_sequences
        min_values = all_events.min()
        max_values = all_events.max()
        team_events = all_events.values.tolist()

        max_values_dict = {}
        max_values_dict['range'] = max_values["range"]
        max_values_dict['capacity'] = max_values["capacity"]
        max_values_dict['cost'] = max_values["cost"]
        max_values_dict['no_structures'] = 7    # based on the designer sequence database
        max_values_dict['no_motors'] = 18
        max_values_dict['no_foils'] = 10
        max_values_dict['no_components'] = 19

        for team_event in team_events:
            seq_id = str(team_event[0])
            drone_config = str(team_event[1]).split(",")[0]
            first_event = False
            event_type = team_event[2]
            if seq_id not in seq_open_distance:
                seq_open_distance[seq_id] = self.MAXVALUE
                seq_start_and_submit[seq_id] = self.MAXVALUE
                seq_first_event_distance[seq_id] = self.MAXVALUE
                seq_scores_preferences[seq_id] = []
                seq_scores_requirements[seq_id] = []
                seq_first_event_type[seq_id] = event_type
                first_event = True


            vehicle_values = {}
            vehicle_values['range'] = max(0, team_event[3])
            vehicle_values['capacity'] = team_event[4]
            vehicle_values['cost'] = team_event[5]
            vehicle_values['no_structures'] = drone_config.count("0")
            vehicle_values['no_motors'] = drone_config.count("1") + drone_config.count("2")
            vehicle_values['no_foils'] = drone_config.count("3")
            vehicle_values['no_components'] = vehicle_values['no_structures'] + vehicle_values['no_motors'] + vehicle_values['no_foils']

            # get Start and Open sequences that are close to the starting number, if not close, then keep them at a max value
            if first_event:
                d = ((((vehicle_values['range'] - starting_range)/(max_values_dict['range'] - min_values["range"]))**2 + \
                    ((vehicle_values['capacity'] - starting_capacity)/(max_values_dict['capacity'] - min_values["capacity"]))**2 + \
                    ((vehicle_values['cost'] - starting_cost)/(max_values_dict['cost'] - min_values["cost"]))**2)**0.5)/1.73
                if "Open" in event_type and d < 0.1:
                    seq_open_distance[seq_id] = d
                elif d < 0.1:
                    seq_first_event_distance[seq_id] = d

            # if a submit and not a sequence that starts with an open
            if "Submit" in event_type and "Open" not in seq_first_event_type[seq_id]:
                seq_start_and_submit[seq_id] = 0

            # task 1 interventions, prefer goal based, since weighted sums can result in different result for small weight changes
            # for concave spaces like range and capacity
            preference_distance = 0
            scaling_factor = 0
            for var_name in pref_values:
                if pref_values[var_name] != self.NOPREFERENCE:
                    if pref_type == 0:
                        preference_distance += -pref_values[var_name]*vehicle_values[var_name]/max_values_dict[var_name]   # smaller better is better for sort , so negative to maximize preference
                        scaling_factor = 1  # assume weights are normalized to 1
                    elif pref_type == 1:
                        preference_distance += ((vehicle_values[var_name] - pref_values[var_name])/max(max_values_dict[var_name], pref_values[var_name]))**2
                        scaling_factor += 1


            if pref_type == 1:
                # for goal-based, adjust distance then divide by square root of diaogaonal for 0-1 ,
                # adjust so final preference value is [-1,0]
                preference_distance = (preference_distance**0.5)/(max(scaling_factor,1)**0.5)
                preference_distance = -1 + preference_distance

                # if Submit, add to preference list, add 0.75 to get top close designs , but also score unsubmitted sequences events 0 to not always get perfect submits event sequences (tunable parameter)
                if "Submit" in event_type:
                    seq_scores_preferences[seq_id].append(preference_distance + 0.75)
                else:
                    seq_scores_preferences[seq_id].append(0)
            elif pref_type == 0:            # this value could be anywhere from -1 to 1, so scale for now and and rescale below, if all preferences are like 0.1-0.5, compared to -0.6 to -0.3, then this gets tricky, so the below calcaultions are used
                if "Submit" in event_type:
                    seq_scores_preferences[seq_id].append(preference_distance)

            # if feasible, 0 score, if infeasible, distance of infeasibility should correspond to norm_distance from constraints
            # task 2 : designer requirements
            norm_distance = 0
            total_quantity = 0
            for var_name in req_values:
                if req_values[var_name][0] != self.MINVALUE or req_values[var_name][1] != self.MAXVALUE:
                    norm_distance += self.constraint_penalty(vehicle_values[var_name], req_values[var_name][0], req_values[var_name][1], max_values_dict[var_name])
                    total_quantity += 1

            # reward a feasible Submit
            # penalize a infeasible Submit
            # get closest
            if norm_distance == 0 and total_quantity > 0 and "Submit" in event_type:
                seq_scores_requirements[seq_id].append(-10)  # reward a feasible submit , maybe even thry and reward this some more
            elif norm_distance > 0 and total_quantity > 0 and "Submit" in event_type:
                seq_scores_requirements[seq_id].append(10 + norm_distance/total_quantity)  # penalize a submit outside of the range
            else:
                seq_scores_requirements[seq_id].append(norm_distance/max(total_quantity,1))

        # weighted sums , scaling to try and be aroud -0.25 (good) to 0.75 bad, assign a 0 value for event sequences without a Submit
        # try and rescale weighted sums preferences to about the same scale as goal-based (-0.25 for good and 0.75 worse)
        # combining weighted sums and preferences and constraints is tricky, along with possibly including other events besides submits
        if pref_type == 0:
            min_pref = self.MAXVALUE
            max_pref = self.MINVALUE
            for seq in seq_scores_preferences:
                if len(seq_scores_preferences[seq]) > 0:
                    min_pref = min(min(seq_scores_preferences[seq]), min_pref)
                    max_pref = max(max(seq_scores_preferences[seq]), max_pref)
            for seq in seq_scores_preferences:
                if len(seq_scores_preferences[seq]) > 0:
                    seq_scores_preferences[seq] = [(((x - min_pref) / (max_pref - min_pref)) - 0.25) for x in seq_scores_preferences[seq]]
                else:
                    seq_scores_preferences[seq] = [0]


        return seq_open_distance, seq_first_event_distance, seq_start_and_submit, seq_scores_preferences, seq_scores_requirements


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
                self.sample_planner(usr, True)
            elif self.team_role[usr] == "business":
                self.sample_business(usr)

        # add adaptive resamples
        self.register_action_in_queue("session", 5, "adaptive")
        self.register_action_in_queue("session", 10, "adaptive")
        self.register_action_in_queue("session", 15, "adaptive")

    def constraint_penalty(self, value, min_value, max_value, total_bound):
        score = 0
        if value < min_value:
            score = (min_value - value)/total_bound
        elif value > max_value:
            score = (value - max_value)/total_bound
        return score

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
                self.sample_planner(usr, False)

    # get the closest session plan to the target plan metrics
    def get_close_plan(self, usr, profit, startupCost, no_deliveries, business_role):

        closest_distance = self.MAXVALUE

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
            closest_distance = dist_scores[sorted_indices[0]]
            if business_role:
                close_plan = plans[int(sorted_indices[0])]
                # make sure it has some profit
                if self.plan_cache[close_plan.id][1] <= 0:
                    close_plan = None
            else:
                # biad selection based on proximity
                selected_ind = max(0,int(self.linear_trend(1.0, -1.0, 0, min(5, len(sorted_indices)), 1)[0]))
                close_plan = plans[int(sorted_indices[selected_ind])]

        return close_plan, closest_distance

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
                if "Business" in user_positions[user_pos].position.role.name:
                    pref_vars = self.business_variables
                elif "Plan" in user_positions[user_pos].position.role.name:
                    pref_vars = self.planner_variables
                else:
                    pref_vars = self.designer_variables
                for var_name in pref_vars:
                    new_preference_setup = DigitalTwinPreference.objects.create(digital_twin=digital_twin_user_setup)
                    new_preference_setup.name = var_name
                    new_preference_setup.pref_value = 0
                    new_preference_setup.save()

                    new_requirement_setup = DigitalTwinRequirement.objects.create(digital_twin=digital_twin_user_setup)
                    new_requirement_setup.name = var_name
                    new_requirement_setup.lower_limit = 0
                    new_requirement_setup.upper_limit = 1000000
                    new_requirement_setup.save()

                    print( "created " + var_name, user_positions[user_pos].position.role.name)

            else:
                digital_twin_setups.append(digital_twin_user_position_query.first())

        return digital_twin_setups

    def preference_example(self):

        prefs = {'channel' : 'twin',
            'type' : 'twin.pref',
            'session_id' : self.session.id,
            'prefs' : [                     # the below result in close approaximation to planners and designers to historical trends, with underperforming a bit in the final selected business plan
#                {
#                    'user_id' : 'arl_1',
#                    'pref_type' : 1,
#                    'profit' : 8000,
#                    'no_customers' : 35
#                },
#                {
#                    'user_id' : 'arl_4',
#                    'pref_type' : 0,
#                    'profit' : 0.9,
#                    'no_customers' : 0.1
#                }
            ], 'reqs' : [
                {
                    'user_id' : 'arl_4',
                    'cost' : {
                        'min' : 10000,
                        'max' : 15000
                    }
                }
            ]
        }

        return json.dumps(prefs)


    def uncertainty_example(self):

        uncertainties = {'channel' : 'twin',
            'type' : 'twin.uncertainty',
            'session_id' : self.session.id,
            'uncertainties' : [                     # the below result in close approaximation to planners and designers to historical trends, with underperforming a bit in the final selected business plan
                {
                    'x' : -0.8,
                    'z' : 6.4,
                    'deviation' : 1.0
                },
                {
                    'x' : -0.7,
                    'z' : 7.2,
                    'deviation' : 2.0
                },
            ]
        }

        return json.dumps(uncertainties)

    def set_uncertainties(self, session, uncertainty_info):

        # get database helper and user roles
        db_helper = DatabaseHelper(session)
        user_positions = db_helper.get_user_positions()
        # for each user, and database objects
        for user_pos in user_positions:
            if "Business" in user_positions[user_pos].position.role.name:
                try:
                    db_helper.set_user_name(user_positions[user_pos].user.username)
                    uncertainty_dict = json.loads(uncertainty_info)
                    db_helper.add_uncertainty_to_scenario(uncertainty_dict)
                    twin_uncertainty_message(session.id, "uncertainty_set")
                except Exception as e:
                    traceback.print_exc()
                    twin_uncertainty_message(session.id, json.dumps({
                        'uncertainty_error' : str(e)
                    }))

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
            print("msg", pref_info)
            for pref in prefs:
                user_id = pref['user_id']
                if user_id in user_roles and user_id in user_positions:
                    digital_twin = DigitalTwin.objects.filter(user_position=user_positions[user_id]).first()
                    role_metrics = []
                    if 'Business' in user_roles[user_id]:
                        role_metrics = self.business_variables
                    elif 'Plan' in user_roles[user_id]:
                        role_metrics = self.planner_variables
                    elif 'Design' in user_roles[user_id]:
                        role_metrics = self.designer_variables
                    for var_name in role_metrics:
                        if var_name in pref:
                            twin_preference = DigitalTwinPreference.objects.filter(Q(digital_twin=digital_twin)&Q(name=var_name)).first()
                            twin_preference.pref_value = pref[var_name]
                            twin_preference.pref_type = pref['pref_type']
                            twin_preference.save()
                            print("set_pref", user_id, var_name, pref[var_name], pref['pref_type'])
                    twin_info_message(session.id, "added preference for " + user_id)
                else:
                    raise Exception("user id invalid")


            reqs = preference_dict['reqs']
            print('reqs updated', reqs)
            for req in reqs:
                user_id = req['user_id']
                print('user_id', user_id)
                if user_id in user_roles and user_id in user_positions:
                    digital_twin = DigitalTwin.objects.filter(user_position=user_positions[user_id]).first()
                    role_metrics = []
                    if 'Business' in user_roles[user_id]:
                        role_metrics = self.business_variables
                    elif 'Plan' in user_roles[user_id]:
                        role_metrics = self.planner_variables
                    elif 'Design' in user_roles[user_id]:
                        role_metrics = self.designer_variables
                    for var_name in role_metrics:
                        if var_name in req:
                            twin_requirement = DigitalTwinRequirement.objects.filter(Q(digital_twin=digital_twin)&Q(name=var_name)).first()
                            twin_requirement.lower_limit = req[var_name]['min']
                            twin_requirement.upper_limit = req[var_name]['max']
                            twin_requirement.save()
                            print("set_req", user_id, var_name, req[var_name]['min'], req[var_name]['max'], twin_requirement.id)
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

    # export to export session data to data logs
    def export_data(self, s):
        with open("data.txt", "a") as myfile:
            myfile.write(s + "\n")
            myfile.close()
