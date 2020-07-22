from __future__ import unicode_literals, print_function, division

import json
from .util.utils import *
from .util.constants import *
from .seq2sql.model.seq2sql import Seq2SQL
from django.conf import settings

import pandas as pd
import pickle
import time

def replace_keywords(s):
    s = s.replace("payload", "capacity")
    s = s.replace("weight", "capacity")
    s = s.replace("lbs", "capacity")
    s = s.replace("lb", "capacity")
    s = s.replace("distance", "range")
    s = s.replace("far", "range")
    s = s.replace("price", "cost")
    s = s.replace("purchase", "cost")
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
            new_query_tokens.append(">")
            new_query_tokens.append(str(float(tokens[int(idx) + 1]) - 0.1))
            new_query_tokens.append("and")
            new_query_tokens.append(tokens[int(idx) - 1])
            new_query_tokens.append("<")
        else:
            new_query_tokens.append(t)

    s = ''
    for token in new_query_tokens:
        s += token + ' '

    return s

class DroneBotSeqToSQL(object):
    model = None

    @classmethod
    def run(cls, question):
        start_time = time.time()
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
        token_question = question.lower().split();
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
        idx = result.find("WHERE")
        stInx = len(result) - idx - 6;
        query_str = result[-stInx:]
        try:
            query_str = fix_query(query_str)
            query_str = convert_equals(query_str)
            print(query_str)
            q1 = pd.read_csv (r'static/ai/designerAI.csv').query(query_str)
            results = []
            if q1.empty:
                print("found no records")
            else:
                q = q1.sample(n=5,replace=False).values.tolist()
                for row in q:
                    print(row)
                    results.append(row)
            return results
        except Exception as e:
            print(e)
            return results
