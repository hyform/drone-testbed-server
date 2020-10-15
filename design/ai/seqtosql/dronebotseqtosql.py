from __future__ import unicode_literals, print_function, division, absolute_import

import json
from .util.utils import *
from .util.constants import *
from .seq2sql.model.seq2sql import Seq2SQL
from django.conf import settings
from repo.models import DataLog

import pandas as pd
import pickle
import time
from random import shuffle

def replace_keywords(s):
    s = s.replace("payload", "capacity")
    s = s.replace("weight", "capacity")
    s = s.replace("lbs", "capacity")
    s = s.replace("lb", "capacity")
    s = s.replace("distance", "range")
    s = s.replace("far", "range")
    s = s.replace("fly", "range")
    s = s.replace("price", "cost")
    s = s.replace("purchase", "cost")
    s = s.replace("drone", "vehicle")
    s = s.replace("design", "vehicle")
    return s

def fix_query(s):
    s = s.replace("Cost", "cost")
    s = s.replace("Range", "range")
    s = s.replace("Velocity", "velocity")
    s = s.replace("Capacity", "capacity")
    s = s.replace("AND", "and")
    s = s.replace("OR", "or")

    # sometimes unit are included
    s = s.replace("miles", "")
    s = s.replace("lbs", "")
    s = s.replace("$", "")
    s = s.replace("pounds", "")

    return s

def convert_equals(s):
    tokens = s.split()
    new_query_tokens = []
    for idx, t in enumerate(tokens):
        if t == "=":
            new_query_tokens.append(">=")
            new_query_tokens.append(str(float(tokens[int(idx) + 1]) - 0.1))
            new_query_tokens.append("and")
            new_query_tokens.append(tokens[int(idx) - 1])
            new_query_tokens.append("<=")
        else:
            new_query_tokens.append(t)

    s = ''
    for token in new_query_tokens:
        s += token + ' '

    return s

class DroneBotSeqToSQL(object):
    model = None

    @classmethod
    def run(cls, question, user=None, session=None):

        # check for Market 2 cost question
        #
        # Dronebot works off one the Market 1 cost scale, so
        # cost needs to be scaled to Market 2
        #
        # if there is cost in the question and a number larger
        # than 1000, than assume it is cost, to scale to the new
        # cost scale (1/0.7)
        market2_cost_bad_response = ""
        if session is not None:
            if session.market.name == "Market 2":
                market2_cost_bad_response = "I could not find any designs that match my generated query for : " + question
                question_lower = question.lower()
                if "cost" in question_lower:
                    question_tokens = question_lower.split()
                    question = ""
                    for token in question_tokens:
                        if token.isnumeric():
                            if float(token) > 1000: # assume a cost value
                                question += str(int(float(token)*(1/0.7))) + " "
                            else:
                                question += token + " "
                        else:
                            question += token + " "


        start_time = time.time()
        results = []
        msg = ''
        if cls.model is None:
            word_embed_file = settings.SEQ2SQL_DATA + '/' + 'word_embed.pkl'
            with open(word_embed_file, 'rb') as handle:
                word_emb = pickle.load(handle)
            cls.model = Seq2SQL(word_emb, N_word=300)
            print("done loading word embedding")

            # load torch model
            agg_m = 'static/ai/seq2sql.agg_model'
            sel_m = 'static/ai/seq2sql.sel_model'
            cond_m = 'static/ai/seq2sql.cond_'

            cls.model.agg_pred.load_state_dict(torch.load(agg_m, map_location='cpu'))
            cls.model.sel_pred.load_state_dict(torch.load(sel_m, map_location='cpu'))
            cls.model.cond_pred.load_state_dict(torch.load(cond_m, map_location='cpu'))
            print('torch models loaded')
            #  set the model to evaluate mode
            cls.model.eval()

        next_time = time.time()

        sql_data = [{'phase': 1, 'table_id': '1-10015132-16', 'question': 'What clu was in toronto 1995-96', 'sql': {'sel': 5, 'conds': [[4, 0, '1995-96']], 'agg': 0}, 'tokenized_query': ['SELECT', 'school/club', 'team', 'FROM', 'table_', 'WHERE', 'years', 'in', 'toronto', 'EQL', '1995-96'], 'query': 'SELECT school/club team FROM table_ WHERE years in toronto EQL 1995-96', 'tokenized_question': ['what', 'clu', 'was', 'in', 'toronto', '1995-96']}, {'phase': 1, 'table_id': '2-19007736-2', 'question': 'What vehicles have more range than 20', 'sql': {'sel': 0, 'conds': [[0, 1, 12]], 'agg': 0}, 'tokenized_query': ['SELECT', 'range', 'FROM', 'table_', 'WHERE', 'range', 'GT', '12'], 'query': 'SELECT range FROM table_ WHERE range GT 12', 'tokenized_question': ['what', 'vehicles', 'have', 'more', 'range', 'than', '20']}]
        table_data = {'1-10015132-16': {'header': ['Player', 'No.', 'Nationality', 'Position', 'Years in Toronto', 'School/Club Team'], 'page_title': 'Toronto Raptors all-time roster', 'types': ['text', 'text', 'text', 'text', 'text', 'text'], 'id': '1-10015132-16', 'section_title': 'R', 'caption': 'R', 'rows': [['Aleksandar Radojević', '25', 'Serbia', 'Center', '1999-2000', 'Barton CC (KS)'], ['Shawn Respert', '31', 'United States', 'Guard', '1997-98', 'Michigan State'], ['Quentin Richardson', 'N/A', 'United States', 'Forward', '2013-present', 'DePaul'], ['Alvin Robertson', '7, 21', 'United States', 'Guard', '1995-96', 'Arkansas'], ['Carlos Rogers', '33, 34', 'United States', 'Forward-Center', '1995-98', 'Tennessee State'], ['Roy Rogers', '9', 'United States', 'Forward', '1998', 'Alabama'], ['Jalen Rose', '5', 'United States', 'Guard-Forward', '2003-06', 'Michigan'], ['Terrence Ross', '31', 'United States', 'Guard', '2012-present', 'Washington']], 'name': 'table_10015132_16', 'page_id': None, 'tokenized_header': [['player'], ['no', '.'], ['nationality'], ['position'], ['years', 'in', 'toronto'], ['school/club', 'team']]}, '2-19007736-2': {'header': ['Range', 'Capacity', 'Cost', 'Config'], 'page_title': 'Vira Rebryk', 'types': ['real', 'real', 'real', 'text'], 'id': '2-19007736-2', 'section_title': 'Vehicles', 'caption': 'Vehicles', 'rows': [['10', '10', '10', '10', 'amm0++']], 'name': None, 'page_id': 19007737.0, 'tokenized_header': [['range'], ['capacity'], ['cost'], ['config']]}}

        # convert to lower case and tokenize
        convert_question = replace_keywords(question.lower())
        token_question = convert_question.split();
        sql_data[1]['tokenized_question'] = token_question

        perm = list(range(len(sql_data)))
        start = 0
        while start < len(sql_data):

            end = start + BATCH_SIZE if start + BATCH_SIZE < len(perm) else len(perm)
            q_seq, col_seq, col_num, ans_seq, query_seq, ground_truth_cond_seq, raw_data =\
                generate_batch_sequence(sql_data, table_data, perm, start, end)

            raw_q_seq = [x[0] for x in raw_data]
            raw_col_seq = [x[1] for x in raw_data]

            table_ids = ['1-10015132-16', '2-19007736-2']
            score = cls.model.forward(q_seq, col_seq, col_num)
            pred_queries = cls.model.gen_query(score, q_seq, col_seq,
                                           raw_q_seq, raw_col_seq)
            result = cls.model.save_readable_results(pred_queries, table_ids, table_data)

            start = end

        # get the results
        print(result)
        # split the query into tokens
        str_array = result.split()
        # replace the specific field queries with * (all)
        str_array[1]='*'
        # replace the nonsense table name with a "real" one
        str_array[3]='ai_designer1'
        q_string = " "
        q_string = q_string.join(str_array)
        print(q_string)
        idx = result.find("WHERE")
        stInx = len(result) - idx - 6;
        query_str = result[-stInx:]
        try:

            print(query_str)

            query_str = fix_query(query_str)
            q_string = fix_query(q_string)
            query_str = convert_equals(query_str)
            designer_db = pd.read_csv (r'static/ai/designerAI.csv')

            # get ranges for all variables for normalization
            min_values = designer_db.min()
            max_values = designer_db.max()

            # query
            q1 = designer_db.query(query_str)

            # if just one design
            if len(q1.values.tolist()) == 1:
                return q1.values.tolist(), "I found a design to show you."

            if q1.empty:
                msg = "I could not find any designs that match my generated query of " + query_str
                if market2_cost_bad_response != "":
                    msg = market2_cost_bad_response
                print("found no records")
            else:

                # query DataLog for dronebot designs
                dronebot_designs = {}
                if user is not None and session is not None:
                    allLogs = DataLog.objects.filter(user = user, session = session).all()
                    for log in allLogs:
                        if "SelectedDroneBotDesign" in log.action:
                            dronebot_designs[log.id] = log.action

                # get preferred designs based on previous selections
                if len(dronebot_designs) > 0:

                    all_distances = []
                    for i in q1.index:
                        all_distances.append(0)

                    # assume id of logs are incremented up to get the latest sel;ect id
                    sorted_by_id = sorted(dronebot_designs, reverse=True)

                    only_first = False
                    attractors_to_include = range(len(sorted_by_id))
                    if only_first:
                        attractors_to_include = range(1)

                    for ii in attractors_to_include:
                        latest_drone_botdesign = dronebot_designs[sorted_by_id[ii]]
                        tokens = latest_drone_botdesign.split(';')
                        range_vehicle = float(tokens[2].split('=')[1])
                        capacity_vehicle = float(tokens[3].split('=')[1])
                        cost_vehicle = float(tokens[4].split('=')[1])

                        #print("attractor at " + str(range_vehicle) + " " + str(capacity_vehicle) + " " + str(cost_vehicle))

                        counter = 0
                        for i in q1.index:
                            norm_distance = (((range_vehicle - float(q1.at[i,'range']))/(max_values["range"] - min_values["range"]))**2 + \
                                ((capacity_vehicle - float(q1.at[i,'capacity']))/(max_values["capacity"] - min_values["capacity"]))**2 + \
                                ((cost_vehicle - float(q1.at[i,'cost']))/(max_values["cost"] - min_values["cost"]))**2)**0.5

                            scale_decay = 2   # making this larger will bias towards the latestes attractor more
                            scaling_factor_att = ((1.0*len(attractors_to_include) - ii)/len(attractors_to_include))**scale_decay
                            all_distances[counter] += norm_distance*scaling_factor_att

                            counter += 1


                    min_value = min(all_distances)
                    max_value = max(all_distances)

                    weights = []
                    # bias towards closer designs
                    for d in all_distances:
                        weights.append(1.0 - ((d - min_value)/(max_value - min_value)))

                    sortedweights = sorted(weights, reverse=True)

                    # randomly choose from top 20
                    min_weight = sortedweights[min(20, len(sortedweights) - 1)]
                    for ii in range(len(weights)):
                        if weights[ii] < min_weight:
                            weights[ii] = 0

                    # choose designs based on weights
                    q = q1.sample(n=min(len(q1) - 1, 5),replace=False, weights=weights).values.tolist()

                else:

                    q = q1.sample(n=min(len(q1), 5),replace=False).values.tolist()


                for row in q:
                    print(row)
                    results.append(row)
                msg = "I found some designs to show you."
            return results, msg
        except Exception as e:
            print(e)
            msg = "<b>Examples</b>:<br> What designs have a range of bigger than 10 ? \
                <br>What vehicles have a cost of smaller than 5000 ?<br>What drones have a \
                capacity of 10 ?<br>What designs have a range bigger than 10 and cost smaller \
                than 5000 ?<br>What vehicles have a range bigger than 10 and capacity bigger \
                than 20 ?<br>What drones have a capacity bigger than 20 and cost smaller than \
                5000 ?<br>range of 10<br>range bigger than 20<br>cost smaller than 5000<br>capacity \
                bigger than 20<br><b>Sorry, I am unable to answer your question. Try again, I \
                usually understand the above questions and commands pretty well.</b><br>"
            return results, msg
