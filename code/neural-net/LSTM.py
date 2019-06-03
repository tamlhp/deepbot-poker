#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 17:27:15 2019

@author: cyril
"""

import mkl
mkl.set_num_threads(1)

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optima
import time
from functools import reduce
from utils import comp_tot_params, get_flat_params, get_dict_sizes, get_full_dict, get_sep_dicts
import pickle
import random

class Net(nn.Module):
    def __init__(self, i_opp, i_gen):
        super(Net, self).__init__()
        self.LSTM_opp = nn.LSTM(input_size =8, hidden_size = 50, num_layers=1)
        self.LSTM_gen = []
        for i in range(10):
            self.LSTM_gen.append(nn.LSTM(8, 10))
        self.LSTM_gen = nn.ModuleList(self.LSTM_gen)
        self.lin_dec_1 = nn.Linear(150, 75)
        self.lin_dec_2 = nn.Linear(75, 1)
        self.i_opp = i_opp
        self.i_gen = i_gen

    def forward(self, x):
        x_opp_out, (self.i_opp['h0'], self.i_opp['c0']) = self.LSTM_opp(x, (self.i_opp['h0'], self.i_opp['c0']))
        x_opp_out = self.LSTM_opp(x)
        x_gen_all, (self.i_gen['h0_0'], self.i_gen['c0_0']) = self.LSTM_gen[0](x, (self.i_gen['h0_0'], self.i_gen['c0_0']))
        for i in range(1,10):
            x_gen, (self.i_gen['h0_'+str(i)], self.i_gen['c0_'+str(i)]) = self.LSTM_gen[i](x, (self.i_gen['h0_'+str(i)], self.i_gen['c0_'+str(i)]))
            #x_gen_all = torch.cat((x_gen_all,self.LSTM_gen[i](x, (i_gen['h0_'+str(i)].view(1,1,10), i_gen['c0_'+str(i)].view(1,1,10)))[0].view(1,1,1,-1)),0)
            x_gen_all = torch.cat((x_gen_all,x_gen),0)

        x_gen_out = x_gen_all.view(1,1,-1)
        x_lin_h = self.lin_dec_1(torch.cat((x_gen_out,x_opp_out[0]),2))
        x_out = self.lin_dec_2(x_lin_h)
        return x_out
    
class LSTM_agent():
    def __init__(self, full_dict):

        if full_dict == None:
            i_opp = self.init_i_opp()
            i_gen = self.init_i_gen()
            self.model = Net(i_opp,i_gen)
            self.state_dict = next(self.model.modules()).state_dict()   #weights are automaticaly generated
        else:
            self.state_dict, i_opp, i_gen = get_sep_dicts(full_dict)
            self.model = Net(i_opp,i_gen)

        
    def init_i_opp(self):
        i_opp_keys = ['h0','c0']
        i_opp = {}
        for key in i_opp_keys:
            i_opp[key]=torch.randn(50).view(1,1,50)
        return i_opp
    
    def init_i_gen(self):
        i_gen_keys = ['h0_'+str(i) for i in range(10)]+['c0_'+str(i) for i in range(10)]
        i_gen = {}
        for key in i_gen_keys:
            i_gen[key]=torch.randn(10).view(1,1,10)
        return i_gen
    
    def predict(self, input_tensor):
        output = self.model(input_tensor)
        return output

"""

# Getting back the state of weight:
with open('full_dict'+str(iter_)+str(agent_no)+'.pkl', 'rb') as f:  
    full_dict = pickle.load(f)
state_dict, i_opp, i_gen = get_sep_dicts(full_dict)
next(model.modules()).load_state_dict(state_dict)


def initialize(agent_no):
    full_dict = state_dict.copy()
    full_dict.update(i_opp), full_dict.update(i_gen)    
    # writing the full dict:
    with open('full_dict_0_'+str(agent_no)+'.pkl', 'wb') as f:  
        pickle.dump(full_dict, f)
    if(agent_no == 0):
        dict_sizes = get_dict_sizes(state_dict, i_opp, i_gen)
        # writing the dict sizes for later reconstruction:
        with open('dict_sizes.pkl', 'wb') as f:  
            pickle.dump(dict_sizes, f)
    return

random.seed(20)
input_tensor = torch.Tensor([random.random() for i in range(8)]).view(1, 1, -1)
#h_opp_0 = torch.Tensor([random.random() for i in range(50)]).view(1, 1, -1)
h_opp_0 = torch.randn(1, 1, 50)
c_opp_0 = torch.randn(1, 1, 50)


print(output.squeeze())






params = get_params(full_dict)
print(all_params.shape)

new_state_dict, new_i_opp, new_i_gen = get_dicts(all_params, dict_sizes)

###save state dict
network = next(model.modules())                 #todo, see if we want to generate weights ourselves
#saved_state_dict = network.state_dict()
"""
my_first_agent = LSTM_agent(None)
input_tensor = torch.Tensor([random.random() for i in range(8)]).view(1, 1, -1)
o1 = my_first_agent.predict(input_tensor)
o2 = my_first_agent.predict(input_tensor)

# writing down the model:
with open('my_first_agent.pkl', 'wb') as f:  
    pickle.dump(my_first_agent, f)

o3 = my_first_agent.predict(input_tensor)   
print(o3)
full_dict_first = my_first_agent.state_dict.copy()
full_dict_first.update(my_first_agent.model.i_opp), full_dict_first.update(my_first_agent.model.i_gen)

    
# Getting back the model:
with open('my_first_agent.pkl', 'rb') as f:
    my_second_agent = pickle.load(f)

o4= my_second_agent.predict(input_tensor)
print(o4)
full_dict_second = my_second_agent.state_dict.copy()
full_dict_second.update(my_second_agent.model.i_opp), full_dict_second.update(my_second_agent.model.i_gen)
    
print(all(get_flat_params(full_dict_first) == get_flat_params(full_dict_second)))
