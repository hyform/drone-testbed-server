from .aibot import AiBot

import pandas as pd
import json
import random
import math

from ai.models import OpsService
from ai.models import OpsPlan
from repo.serializers import PlanSerializer

from Levenshtein import distance as lev

class OpsBot(AiBot):

    def __init__(self, name, session, db_helper, user):
        super().__init__(name, session, db_helper, user)
        self.name = name
        self.profit = 0
        self.cost = 0
        self.no_customers = 0
        self.db_helper = db_helper
        self.config = ""

        self.ask_adapt_variables = ["profit", "cost", "customers"]

    def get_type(self):
        return "opsbot"

    def adapt_function(self, s):
        vars_included = []
        for var_info in self.variable_info:
            if var_info.variable in self.ask_adapt_variables:
                self.ask_adapt_variables.remove(var_info.variable)

        for var_name in self.ask_adapt_variables:
            if var_name in s:
                self.ask_adapt_variables.remove(var_name)
        if s == "no":
            self.ask_adapt_variables.pop(0)

        if "profit" in self.ask_adapt_variables:
            return ["Do you have any preference on profit ?"]
        if "cost" in self.ask_adapt_variables:
            return ["Do you have any preference on cost ?"]
        if "customers" in self.ask_adapt_variables:
            return ["Do you have any preference on customers ?"]
        self.adapt = False
        self.command = "want"
        return None

    def receive_message(self, s, channel, usr):

        if "help" in s:
            self.response = []
            self.response.append("Send commands with profit, cost, customers, values, reference plans, and direction. Some examples are")
            self.response.append("want higher profit")
            self.response.append("want lower cost than 10000")
            self.response.append("want higher profit and higher customers than 6")
            self.response.append("@ref_plan_name : want higher profit")
            self.response.append("want higher profit north east")
            self.response.append("want lower cost south")
            return self.response


        # unsatisfied, keep old preference and command
        if "unsatisfied" in s:
            self.response = []
            self.response.append("Can you provide guidance on what you are unsatisfied about with respect to profit, cost, or number of customers ? ")
            return self.response

        if "suggestion" in s:
            return self.suggestion_alg()

        # set grammar-based variables
        if "iterate" not in s:
            super().receive_message(s, channel, usr)
            if self.adapt:
                res = self.adapt_function(s)
                if res is not None:
                    return res

        geo_locations = []
        tokens = s.split()
        if "north" in tokens:
            geo_locations.append("north")
        if "south" in tokens:
            geo_locations.append("south")
        if "east" in tokens:
            geo_locations.append("east")
        if "west" in tokens:
            geo_locations.append("west")

        # print bot grammer information
        print("grammar input", self.command)
        print("grammar input command", self.referenced_obj)
        for var_info in self.variable_info:
            print("grammar input variable", var_info.pref_dir, var_info.variable, var_info.value )

        # current state
        print("current state : profit", self.profit )
        print("current state : cost", self.cost)
        print("current state : no customers", self.no_customers)

        # bot procedures
        # as an example, just chose a random vehicle and run the ai agent
        if 'want' in self.command:

            # copy value for last state reference, so if a someone wants more, than we have a reference
            last_profit = self.profit
            last_cost = self.cost
            last_no_customers = self.no_customers
            last_config = self.config

            # if referencing another plan, then reference that plan
            if self.referenced_obj is not None:
                self.db_helper.set_user_name(self.name)
                ref_query = self.db_helper.query_plans_with_name(self.referenced_obj)
                if ref_query:
                    serializer = PlanSerializer(ref_query[0])
                    plan_str = json.dumps(serializer.data)
                    result = OpsService(plan_str)

                    last_profit = result.profit
                    last_cost = result.startupCost
                    last_no_customers = result.number_deliveries
                    last_config = plan_str

            # submit values, added these since we want to choose the closest plan based on the current plan
            submit_plan = False
            submit_lev_dist = 1000000    # tune this to be samller to do smaller changes
            submit_plan_str = ""
            submit_profit = 0
            submit_cost = 0
            submit_no_customers = 0
            submit_json_plan = None

            vehicle_request_tally = []

            # tuning parameters for effectiveness
            MM = 6#
            for i in range(MM):

                # create the plan input string with empty paths, where each path has a closest vehicle as recommended by the planner AI
                plan = {}
                paths = []

                # set user name
                self.db_helper.set_user_name(self.name)

                # get scenario
                scenario_obj = self.db_helper.get_scenario()

                # reached budget
                fixed_cost = 0
                counter = 0 # to prevent infinite loop
                under_budget = True
                budget = random.randrange(10000, 30000)
                for var_info in self.variable_info:
                    if 'cost' == var_info.variable:
                        value = var_info.value
                        if not math.isnan(value):
                            budget = value

                while under_budget and counter < 100:
                    counter += 1

                    try:

                        vehs = self.db_helper.query_vehicles()
                        used_vehicle = vehs[random.randrange(0, len(vehs))]

                        fixed_cost += used_vehicle.cost
                        if fixed_cost <= budget:
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
                        else:
                            under_budget = False

                    except Exception as e:
                        print(e)

                # add an empty path to the plan
                plan['paths'] = paths
                plan['scenario'] = scenario_obj

                # convert to string for the planner AI
                json_str = json.dumps(plan)

                # use planner agent to create new plan
                o = OpsPlan(json_str, geo_locations)
                plan_ai_json = o.output.replace("\'","\"").replace("True", "true").replace("False", "false")

                # save the plan json object
                json_obj_plan = json.loads(plan_ai_json)

                # convert the json plan to a string to save to a dataLog and calculate metrics and get the metrics of the new plan
                plan_str = json.dumps(json_obj_plan)
                result = OpsService(plan_str)

                # set new values
                self.profit = result.profit
                self.cost = result.startupCost
                self.no_customers = result.number_deliveries
                self.config = json.dumps(json_obj_plan["paths"])

                for vehicle_result in result.path_results:
                    vehicle_request_tally.append(vehicle_result)

                # send a return message (update this) , just an example
                self.response = []
                #self.response.append("calculated intent is : " + s)

                value_specified = False
                # just do some example
                for var_info in self.variable_info:
                    if 'profit' == var_info.variable:
                        pref_dir = var_info.pref_dir
                        value = var_info.value
                        if math.isnan(value):  # maybe apply some kind of delta here
                            value = last_profit
                            value_specified = True
                        if ("lower" in pref_dir or "less" in pref_dir ) and self.profit >= value:
                            self.response.append("ping unsatisfied profit")
                        elif ("higher" in pref_dir or "more" in pref_dir ) and self.profit <= value:
                            self.response.append("ping unsatisfied profit")
                    if 'cost' == var_info.variable:
                        pref_dir = var_info.pref_dir
                        value = var_info.value
                        if math.isnan(value):  # maybe apply some kind of delta here
                            value = last_cost
                            value_specified = True
                        if ("lower" in pref_dir or "less" in pref_dir ) and self.cost >= value:
                            self.response.append("ping unsatisfied cost")
                        elif ("higher" in pref_dir or "more" in pref_dir ) and self.cost <= value:
                            self.response.append("ping unsatisfied cost")
                    if 'customers' == var_info.variable:
                        pref_dir = var_info.pref_dir
                        value = var_info.value
                        if math.isnan(value):  # maybe apply some kind of delta here
                            value = last_no_customers
                            value_specified = True
                        if ("lower" in pref_dir or "less" in pref_dir ) and self.no_customers >= value:
                            self.response.append("ping unsatisfied customers")
                        elif ("higher" in pref_dir or "more" in pref_dir ) and self.no_customers <= value:
                            self.response.append("ping unsatisfied customers")

                if len(self.response) == 0:
                    lev_dist = lev(last_config, self.config)

                    nudge = True
                    # set nudge distance tolerances
                    if not value_specified:
                        nudge = abs(self.profit - last_profit) < 5000 and abs(self.cost - last_cost) < 5000 and abs(self.no_customers - last_no_customers) < 20
                        nudge = nudge and (abs(self.profit - last_profit) > 200 or abs(self.cost - last_cost) > 200 or abs(self.no_customers - last_no_customers) > 2)

                    print('test lev', lev_dist)
                    if lev_dist < submit_lev_dist and nudge:
                        submit_plan = True
                        print('lev', lev_dist)
                        submit_lev_dist = lev_dist
                        submit_config = self.config
                        submit_profit = self.profit
                        submit_cost = self.cost
                        submit_no_customers = self.no_customers
                        submit_json_plan = json_obj_plan

            no_shock = self.session.market.name != "Market 3"
            if submit_plan:

                self.response = []
                #self.response.append("calculated intent is : " + s)

                # set the bot metrics to the submitted values
                self.db_helper.set_user_name(self.name)
                self.config = submit_config
                self.profit = submit_profit
                self.no_customers = submit_no_customers
                self.cost = submit_cost

                # create some kind of id for now
                tag_id = "p" + str(int(self.profit)) + "_$" + str(int(self.cost)) + "_c" + str(int(self.no_customers))
                submit_json_plan['tag'] = tag_id

                # save a submitted design
                plan_obj = self.db_helper.plan_submit(submit_json_plan)
                plan_obj.valid = no_shock
                plan_obj.save()

                self.response.append("I submitted a plan @" + tag_id + ", profit= " + str(round(self.profit, 1)) + ", cost=" + str(round(self.cost, 0)) + ", nocustomers = " + str(int(self.no_customers)) + ". Let me know of any feedback.")
                if not no_shock:
                    self.response.append("A team planner needs to evaluate this plan for it to become usuable")

                # send a return message (update this) , just an example
                return self.response

            # vehicle suggestions
            # get all vehicles
            vehicle_dict = {}
            want_strs = []
            for vehicle_result in vehicle_request_tally:
                vehicle_dict[vehicle_result[0]] = []
            for vehicle_result in vehicle_request_tally:
                vehicle_dict[vehicle_result[0]].append(vehicle_result[1])
            if len(vehicle_dict) > 0:
                want_strs.append("Possible suggestions for additional drone capabilities include the following:")
            for vehicle_tag in vehicle_dict:
                range_occurrences = vehicle_dict[vehicle_tag].count("range_limit")
                capacity_occurrences = vehicle_dict[vehicle_tag].count("capacity_limit")
                if capacity_occurrences > range_occurrences:
                    want_strs.append("@" + vehicle_tag + ": want higher capacity")
                elif range_occurrences > capacity_occurrences:
                    want_strs.append("@" + vehicle_tag + ": want higher range")
                elif range_occurrences > 0: # pick random one
                    want_strs.append("@" + vehicle_tag + ": want higher range")


            responses = self.response
            for want_str in want_strs:
                responses.append(want_str)

            if random.random() < 0.5:


                tag_id = "p" + str(int(self.profit)) + "_$" + str(int(self.cost)) + "_c" + str(int(self.no_customers))
                json_obj_plan['tag'] = tag_id

                # save a submitted design
                plan_obj = self.db_helper.plan_submit(json_obj_plan)
                plan_obj.valid = no_shock
                plan_obj.save()

                self.response.append("I could not create a plan that matched your request, but I submitted a plan @" + tag_id + ", profit=" + str(self.profit) + ", cost=" + str(self.cost) + ", customers=" + str(self.no_customers) + ". Let me know of any feedback.")
                if not no_shock:
                    self.response.append("A team planner needs to evaluate this plan for it to become usuable")


                # send a return message (update this) , just an example
                return self.response


            # reset to last state
            self.profit = last_profit
            self.cost = last_cost
            self.no_customers = last_no_customers
            self.config = last_config

            print(responses)

            return responses

        if 'ping' in self.command and 'status' in self.command_type:
            return ["status : profit = " + str(round(self.profit, 0)) + ", cost = " + str(round(self.cost, 0)) + ", customers = " + str(round(self.no_customers, 0))]

    def save_cache(self):
        # save a submitted design
        # get the last id in the channel vehicles
        print("save cahce")

    def suggestion_alg(self):

        lev_dist = 100000000
        last_config = self.config
        submit_json_plan = None

        MM = 10#
        for i in range(MM):

            # create the plan input string with empty paths, where each path has a closest vehicle as recommended by the planner AI
            plan = {}
            paths = []

            # set user name
            self.db_helper.set_user_name(self.name)

            # get scenario
            scenario_obj = self.db_helper.get_scenario()

            # reached budget
            fixed_cost = 0
            counter = 0 # to prevent infinite loop
            under_budget = True
            budget = random.randrange(10000, 30000)
            for var_info in self.variable_info:
                if 'cost' == var_info.variable:
                    value = var_info.value
                    if not math.isnan(value):
                        budget = value

            while under_budget and counter < 100:
                counter += 1

                try:

                    vehs = self.db_helper.query_vehicles()
                    used_vehicle = vehs[random.randrange(0, len(vehs))]

                    fixed_cost += used_vehicle.cost
                    if fixed_cost <= budget:
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
                    else:
                        under_budget = False

                except Exception as e:
                    print(e)

            # add an empty path to the plan
            plan['paths'] = paths
            plan['scenario'] = scenario_obj

            # convert to string for the planner AI
            json_str = json.dumps(plan)

            # use planner agent to create new plan
            o = OpsPlan(json_str, [])
            plan_ai_json = o.output.replace("\'","\"").replace("True", "true").replace("False", "false")

            # save the plan json object
            json_obj_plan = json.loads(plan_ai_json)

            # convert the json plan to a string to save to a dataLog and calculate metrics and get the metrics of the new plan
            plan_str = json.dumps(json_obj_plan)

            new_paths = json.dumps(json_obj_plan["paths"])

            test = lev(last_config, new_paths)

            if test < lev_dist:
                lev_dist = test
                result = OpsService(plan_str)
                submit_json_plan = json_obj_plan

                self.profit = result.profit
                self.cost = result.startupCost
                self.no_customers = result.number_deliveries
                self.config = json.dumps(json_obj_plan["paths"])



        no_shock = self.session.market.name != "Market 3"

        self.response = []
        self.db_helper.set_user_name(self.name)

        # create some kind of id for now
        tag_id = "p" + str(int(self.profit)) + "_$" + str(int(self.cost)) + "_c" + str(int(self.no_customers))
        submit_json_plan['tag'] = tag_id

        # save a submitted design
        plan_obj = self.db_helper.plan_submit(submit_json_plan)
        plan_obj.valid = no_shock
        plan_obj.save()

        self.response.append("I submitted a plan @" + tag_id + ", profit= " + str(round(self.profit, 1)) + ", cost=" + str(round(self.cost, 0)) + ", nocustomers = " + str(int(self.no_customers)) + ". Let me know of any feedback.")
        if not no_shock:
            self.response.append("A team planner needs to evaluate this plan for it to become usuable")

        return self.response
