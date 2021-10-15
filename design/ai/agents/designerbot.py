from .aibot import AiBot
from .designermarkov import DesignerMarkov
from .adaptive_team_ai_updated_planner import AdaptiveTeamAIUpdatedPlanner
from Levenshtein import distance as lev

import pandas as pd
import math
import random

class DesignerBot(AiBot):

    def __init__(self, name, session, db_helper, user):
        super().__init__(name, session, db_helper, user)
        self.range = 10
        self.capacity = 5
        self.cost = 3470
        self.velocity = 20
        self.config = "aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3"
        self.ask_adapt_variables = ["range", "capacity", "cost"]

    def get_type(self):
        return "designbot"

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

        if "range" in self.ask_adapt_variables:
            return ["Do you have any preference on range ?"]
        if "capacity" in self.ask_adapt_variables:
            return ["Do you have any preference on capacity ?"]
        if "cost" in self.ask_adapt_variables:
            return ["Do you have any preference on cost ?"]

        self.adapt = False
        self.command = "want"
        return None

####    def receive_message(self, s, channel, channel_instance, channel_layer):
    def receive_message(self, s, channel, usr):

        if "help" in s:
            self.response = []
            self.response.append("Send commands with range, capacity, cost, values, and reference drones. Some examples are")
            self.response.append("want higher range")
            self.response.append("want lower cost than 4000")
            self.response.append("want higher range and higher capacity than 20")
            self.response.append("@ref_drone_name : want higher range")
            self.response.append("suggestion")
            return self.response

        if "unsatisfied" in s:
            self.response = []
            self.response.append("Can you provide guidance on what you are unsatisfied about with respect to range, capacity, or cost ? ")
            return self.response

        if "suggestion" in s:
            last_config = self.config
            lev_dist = 100000000000
            selected_designs = pd.read_csv(r'static/ai/designerAI.csv').values.tolist()
            for selected_design in selected_designs:
                test = lev(last_config, selected_design[4])
                if test < lev_dist:
                    self.range = selected_design[0]
                    self.capacity = selected_design[2]
                    self.cost = selected_design[1]
                    self.config = selected_design[4]
                    self.velocity = selected_design[3]
                    lev_dist = test

            tag_id = "r" + str(int(self.range)) + "_c" + str(int(self.capacity)) + "_$" + str(int(self.cost))
            no_shock = self.session.market.name != "Market 3"
            self.db_helper.set_user_name(self.name)
            self.db_helper.submit_vehicle_db(tag_id, self.config, self.range, self.capacity, self.cost, self.velocity, no_shock)
            self.response.append("I submitted a drone design @" + tag_id +", range= " + str(round(self.range, 1)) + ", capacity=" + str(round(self.capacity, 0)) + ", cost = " + str(int(self.cost)) + ". Let me know of any feedback.")
            if not no_shock:
                self.response.append("A team designer needs to evaluate this design for it to become usuable")

            return self.response

        if "iterate" not in s:
            super().receive_message(s, channel, usr)
            if self.adapt:
                res = self.adapt_function(s)
                if res is not None:
                    return res

        # print bot grammer information
        print("grammar input", self.command)
        print("grammar input type", self.command_type)
        print("grammar input command", self.referenced_obj)
        for var_info in self.variable_info:
            print("grammar input variable", var_info.pref_dir, var_info.variable, var_info.value )

        # current state
        print("current state : range", self.range )
        print("current state : capacity", self.capacity)
        print("current state : cost", self.cost)
        print("current state : velocity", self.velocity )
        print("current state : config", self.config )

        # bot procedures
        # as an example
        if 'want' in self.command:


            # comment this out for global pref
            #if usr not in self.saved_states:
            #    self.saved_states[usr] = [ "aMM0+++++*bNM2+++*cMN1+++*dLM2+++*eML1+++^ab^ac^ad^ae,5,3", 10, 5, 3470]
            #self.config = self.saved_states[usr][0]
            #self.range = self.saved_states[usr][1]
            #self.capacity = self.saved_states[usr][2]
            #self.cost = self.saved_states[usr][3]
            #print("assigned save state ---------------------------------------------- ", usr, self.config, self.range, self.capacity, self.cost )


            # copy value for last state reference, so if a someone wants more, than we have a reference
            last_range = self.range
            last_capacity = self.capacity
            last_cost = self.cost
            last_config = self.config

            # if referencing another design, then reference that design
            if self.referenced_obj is not None:
                self.db_helper.set_user_name(self.name)
                ref_query = self.db_helper.query_vehicles_with_name(self.referenced_obj)
                if ref_query:
                    last_range = ref_query[0].range
                    last_capacity = ref_query[0].payload
                    last_cost = ref_query[0].cost
                    print("reference", last_range, last_capacity, last_cost)


            # submit values, added these since we want to choose the closest design based on the input space
            submit_design = False
            submit_lev_dist = 50    # tune this to be samller to do smaller changes
            submit_config = ""
            submit_range = 0
            submit_capacity = 0
            submit_cost = 0
            submit_velocity = 0

            # tuning parameters for effectiveness
            MM = 400#
            selected_designs = pd.read_csv(r'static/ai/designerAI.csv').sample(n=MM).values.tolist()
            for selected_design in selected_designs:


                # for now select a random design
                # one could perform some preference are requirement selection here
                #selected_design = pd.read_csv(r'static/ai/designerAI.csv').sample(n=1).values.tolist()[0]

                # possible Markov chain implementation
                #test = DesignerMarkov()

                # possible digital twin approaches
                #digitial_twin = AdaptiveTeamAIUpdatedPlanner()
                #digitial_twin.initialize_rnn_seq_data()
                #seq_open_distance, seq_first_event_distance, seq_start_and_submit, seq_scores_preferences, seq_scores_requirements = digitial_twin.get_designer_event_scores(1, {}, {"range" : [20, 30]}, 10, 5, 3470)
                #print(seq_open_distance, seq_first_event_distance, seq_start_and_submit, seq_scores_preferences, seq_scores_requirements)

                # set the current state of the bot to this evaluated design
                self.range = selected_design[0]
                self.capacity = selected_design[2]
                self.cost = selected_design[1]
                self.config = selected_design[4]
                self.velocity = selected_design[3]

                # send a return message (update this) , just an example
                self.response = []
                #self.response.append("calculated intent is : " + s)

                # test save requests
                value_specified = False
                for var_info in self.variable_info:
                    if 'range' == var_info.variable:
                        pref_dir = var_info.pref_dir
                        value = var_info.value
                        if math.isnan(value):  # maybe apply some kind of delta here
                            value = last_range
                        else:
                            value_specified = True
                        if ("lower" in pref_dir or "less" in pref_dir ) and self.range >= value:
                            self.response.append("ping unsatisfied range")
                        elif ("higher" in pref_dir or "more" in pref_dir ) and self.range <= value:
                            self.response.append("ping unsatisfied range")
                    if 'capacity' == var_info.variable:
                        pref_dir = var_info.pref_dir
                        value = var_info.value
                        if math.isnan(value):  # maybe apply some kind of delta here
                            value = last_capacity
                        else:
                            value_specified = True
                        if ("lower" in pref_dir or "less" in pref_dir ) and self.capacity >= value:
                            self.response.append("ping unsatisfied capacity")
                        elif ("higher" in pref_dir or "more" in pref_dir ) and self.capacity <= value:
                            self.response.append("ping unsatisfied capacity")
                    if 'cost' == var_info.variable:
                        pref_dir = var_info.pref_dir
                        value = var_info.value
                        if math.isnan(value):  # maybe apply some kind of delta here
                            value = last_cost
                        else:
                            value_specified = True
                        if ("lower" in pref_dir or "less" in pref_dir ) and self.cost >= value:
                            self.response.append("ping unsatisfied cost")
                        elif ("higher" in pref_dir or "more" in pref_dir ) and self.cost <= value:
                            self.response.append("ping unsatisfied cost")

                # its feasible, gets its input distance and save the closest design that satisfies the requests
                if len(self.response) == 0:
                    lev_dist = lev(last_config, self.config)
                    nudge = True
                    # set nudge distance tolerances
                    if not value_specified:
                        nudge = abs(self.range - last_range) < 20 and abs(self.capacity - last_capacity) < 20 and abs(self.cost - last_cost) < 2000
                        nudge = nudge and (abs(self.range - last_range) > 2 or abs(self.capacity - last_capacity) > 2 or abs(self.cost - last_cost) > 200)
                    if lev_dist < submit_lev_dist and nudge:
                        submit_design = True
                        print('lev', lev_dist, last_config, self.config)
                        submit_lev_dist = lev_dist
                        submit_config = self.config
                        submit_range = self.range
                        submit_capacity = self.capacity
                        submit_cost = self.cost
                        submit_velocity = self.velocity


            # we have a design to submit
            if submit_design:

                self.response = []
                #self.response.append("calculated intent is : " + s)

                # set the bot metrics to the submitted values
                self.db_helper.set_user_name(self.name)
                self.config = submit_config
                self.range = submit_range
                self.capacity = submit_capacity
                self.cost = submit_cost
                self.velocity = submit_velocity

                self.saved_states[usr] = [self.config, self.range, self.capacity, self.cost, self.velocity]

                tag_id = "r" + str(int(self.range)) + "_c" + str(int(self.capacity)) + "_$" + str(int(self.cost))

                no_shock = self.session.market.name != "Market 3"

                # get an id for the vehicle submit
                self.db_helper.submit_vehicle_db(tag_id, self.config, self.range, self.capacity, self.cost, self.velocity, no_shock)
                self.response.append("I submitted a drone design @" + tag_id +", range= " + str(round(self.range, 1)) + ", capacity=" + str(round(self.capacity, 0)) + ", cost = " + str(int(self.cost)) + ". Let me know of any feedback.")
                if not no_shock:
                    self.response.append("A team designer needs to evaluate this design for it to become usuable")




                return self.response  # time delay

            # we could not find a feasible design, but we will submit our last state anyways, tune the 0.5
            if random.random() < 0.5:

                self.response = []
                #self.response.append("calculated intent is : " + s)

                # save a submitted design
                # get the last id in the channel vehicles
                self.db_helper.set_user_name(self.name)

                self.saved_states[usr] = [self.config, self.range, self.capacity, self.cost, self.velocity]

                tag_id = "r" + str(int(self.range)) + "_c" + str(int(self.capacity)) + "_$" + str(int(self.cost))

                self.db_helper.submit_vehicle_db(tag_id, self.config, self.range, self.capacity, self.cost, self.velocity)
                self.response.append("I could not create a drone that matched your request, but I submitted a drone design @" + tag_id + ", range=" + str(self.range)+ ", capacity=" + str(self.capacity) + ", cost=" + str(self.cost) + ". Let me know of any feedback.")
                return self.response  # time delay

            # reset or state to the last design or the referenced vehicle in the command
            self.range = last_range
            self.capacity = last_capacity
            self.cost = last_cost
            self.config = last_config
            self.response.append("ask again if you want me to try harder to see if I can create a design that satisifes your request")

        if 'ping' in self.command and 'status' in self.command_type:
            self.response.append("status : range = " + str(round(self.range, 1)) + " , capacity = " + str(round(self.capacity, 0)) + " , cost = " + str(round(self.cost,0)))

        return self.response
