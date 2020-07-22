import json
import torch
from torch import nn as nn
from torch.autograd import Variable
import numpy as np


def generate_batch_sequence(sql_data, table_data, idxes, start, end):
    """Function creates a batch of input data given starting and ending indices."""
    # A container is created for each component of the input
    question_sequence = []
    column_sequence = []
    number_of_columns = []
    answer_sequence = []
    query_sequence = []
    ground_truth_condition_sequence = []
    raw_data = []
    for i in range(start, end):
        sql = sql_data[idxes[i]]
        question_sequence.append(sql['tokenized_question'])
        column_sequence.append(table_data[sql['table_id']]['tokenized_header'])
        number_of_columns.append(len(table_data[sql['table_id']]['header']))
        answer_sequence.append((sql['sql']['agg'],
                        sql['sql']['sel'],
                        len(sql['sql']['conds']),
                        tuple(x[0] for x in sql['sql']['conds']),
                        tuple(x[1] for x in sql['sql']['conds'])))
        query_sequence.append(sql['tokenized_query'])
        ground_truth_condition_sequence.append(sql['sql']['conds'])
        raw_data.append((sql['question'], table_data[sql['table_id']]['header'], sql['query']))


    return question_sequence, column_sequence, number_of_columns, answer_sequence, query_sequence,\
        ground_truth_condition_sequence, raw_data

def generate_batch_query(sql_data, idxes, start, end):
    query_gt = []
    table_ids = []
    for i in range(start, end):
        query_gt.append(sql_data[idxes[i]]['sql'])
        table_ids.append(sql_data[idxes[i]]['table_id'])
    return query_gt, table_ids


def run_lstm(lstm, inp, inp_len, hidden=None):
    sort_perm = np.array(sorted(range(len(inp_len)), key=lambda k: inp_len[k], reverse=True))
    sort_inp_len = inp_len[sort_perm]
    sort_perm_inv = np.argsort(sort_perm)
    if inp.is_cuda:
        sort_perm = torch.LongTensor(sort_perm).cuda()
        sort_perm_inv = torch.LongTensor(sort_perm_inv).cuda()

    lstm_inp = nn.utils.rnn.pack_padded_sequence(inp[sort_perm],
                                                 sort_inp_len, batch_first=True)
    if hidden is None:
        lstm_hidden = None
    else:
        lstm_hidden = (hidden[0][:, sort_perm], hidden[1][:, sort_perm])

    sort_ret_s, sort_ret_h = lstm(lstm_inp, lstm_hidden)
    ret_s = nn.utils.rnn.pad_packed_sequence(
        sort_ret_s, batch_first=True)[0][sort_perm_inv]
    ret_h = (sort_ret_h[0][:, sort_perm_inv], sort_ret_h[1][:, sort_perm_inv])
    return ret_s, ret_h


def col_name_encode(name_inp_var, name_len, col_len, enc_lstm):
    # Encode the columns.
    # The embedding of a column name is the last state of its LSTM output.
    name_hidden, _ = run_lstm(enc_lstm, name_inp_var, name_len)
    name_out = name_hidden[tuple(range(len(name_len))), name_len - 1]
    ret = torch.FloatTensor(len(col_len), max(col_len), name_out.size()[1]).zero_()
    if name_out.is_cuda:
        ret = ret.cuda()

    st = 0
    for idx, cur_len in enumerate(col_len):
        ret[idx, :cur_len] = name_out.data[st:st + cur_len]
        st += cur_len
    ret_var = Variable(ret)

    return ret_var, col_len
