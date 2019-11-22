#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 12:23:22 2019

@author: cyril
"""

import mkl
mkl.set_num_threads(64)
import os
import numpy as np
import pickle
from bot_LSTMBot import LSTMBot
import random
import torch
from sys import getsizeof
from collections import OrderedDict
from operator import add

def get_flat_params(full_dict):
    params = torch.Tensor(0)
    for key in sorted(full_dict.keys()):
        params = torch.cat((params, full_dict[key].view(-1)),0)
    return params

def get_full_dict(all_params, m_sizes_ref):
    #dict_sizes=get_dict_sizes(m_sizes_ref.state_dict,m_sizes_ref.model.i_opp,m_sizes_ref.model.i_gen)
    dict_sizes=get_dict_sizes(m_sizes_ref.full_dict)
    full_dict = OrderedDict()
    i_start = 0
    for layer in sorted(dict_sizes.keys()):
        full_dict[layer] = torch.Tensor(all_params[i_start:i_start+dict_sizes[layer]['numel']]).view(dict_sizes[layer]['shape'])
        i_start+=dict_sizes[layer]['numel']
    return full_dict


def get_dict_sizes(all_dicts):
    dict_sizes = OrderedDict()
    #all_dicts = state_dict.copy()
    #all_dicts.update(i_opp), all_dicts.update(i_gen)
    for key in all_dicts.keys():
        dict_sizes[key] = {}
        dict_sizes[key]['numel'] = all_dicts[key].numel()
        dict_sizes[key]['shape'] = list(all_dicts[key].shape)
    return dict_sizes

def prep_gen_dirs(dir_):
    if not os.path.exists(dir_):
        os.makedirs(dir_)
    if not os.path.exists(dir_+'/bots'):
        os.makedirs(dir_+'/bots')

def get_gen_flat_params(dir_, ga_popsize = 50):
    #TODO, remove ga_popsize argument (read all files automaticaly)
    all_gen_flat = []
    for bot_id in range(1,ga_popsize+1):
        with open(dir_+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:
            params_flat = pickle.load(f)
            all_gen_flat.append(params_flat)
    return all_gen_flat
