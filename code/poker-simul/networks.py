#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 19:34:51 2019

@author: cyril
"""
from torch import nn
import torch
import numpy as np

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
        self.u_opp = i_opp.copy()
        self.u_gen = i_gen.copy()

    def forward(self, x):
        x_opp_out, (self.u_opp['opp_h0'], self.u_opp['opp_c0']) = self.LSTM_opp(x, (self.u_opp['opp_h0'], self.u_opp['opp_c0']))
        #print('x_opp_out: '+str(x_opp_out[0][0][:20]))
        x_opp_out = self.LSTM_opp(x)
        x_gen_all, (self.u_gen['gen_h0_0'], self.u_gen['gen_c0_0']) = self.LSTM_gen[0](x, (self.u_gen['gen_h0_0'], self.u_gen['gen_c0_0']))
        for i in range(1,10):
            x_gen, (self.u_gen['gen_h0_'+str(i)], self.u_gen['gen_c0_'+str(i)]) = self.LSTM_gen[i](x, (self.u_gen['gen_h0_'+str(i)], self.u_gen['gen_c0_'+str(i)]))
            #x_gen_all = torch.cat((x_gen_all,self.LSTM_gen[i](x, (i_gen['h0_'+str(i)].view(1,1,10), i_gen['c0_'+str(i)].view(1,1,10)))[0].view(1,1,1,-1)),0)
            x_gen_all = torch.cat((x_gen_all,x_gen),0)

        x_gen_out = x_gen_all.view(1,1,-1)
        x_lin_h = torch.tanh(self.lin_dec_1(torch.cat((x_gen_out,x_opp_out[0]),2)))
        x_out = torch.tanh(self.lin_dec_2(x_lin_h))
        return x_out
    
    def reset_u_opp(self):
        self.u_opp = self.i_opp.copy()
    def reset_u_gen(self):
        self.u_gen = self.i_gen.copy()
    def reset(self):
        self.reset_u_opp()
        self.reset_u_gen()
        return
    
    
    
class Net_2(nn.Module):
    def __init__(self, i_opp, i_gen):
        super(Net_2, self).__init__()
        self.LSTM_opp = []
        for i in range(10):
            self.LSTM_opp.append(nn.LSTM(8, 10))
            self.LSTM_opp = nn.ModuleList(self.LSTM_opp)
        
        self.LSTM_gen = []
        for i in range(10):
            self.LSTM_gen.append(nn.LSTM(8, 10))
        self.LSTM_gen = nn.ModuleList(self.LSTM_gen)
        self.lin_dec_1 = nn.Linear(200, 50)
        self.lin_dec_2 = nn.Linear(50, 10)
        self.lin_dec_3 = nn.Linear(10, 1)
        self.i_opp = i_opp
        self.i_gen = i_gen
        self.u_opp = i_opp.copy()
        self.u_gen = i_gen.copy()

    def forward(self, x):
        #x_opp_out, (self.u_opp['h0'], self.u_opp['c0']) = self.LSTM_opp(x, (self.u_opp['h0'], self.u_opp['c0']))
        #print('x_opp_out: '+str(x_opp_out[0][0][:20]))
        #x_opp_out = self.LSTM_opp(x)
        
        #Opponent blocks
        x_opp_all, (self.u_opp['opp_h0_0'], self.u_opp['opp_c0_0']) = self.LSTM_opp[0](x, (self.u_opp['opp_h0_0'], self.u_opp['opp_c0_0']))
        for i in range(1,10):
            x_opp, (self.u_opp['opp_h0_'+str(i)], self.u_opp['opp_c0_'+str(i)]) = self.LSTM_opp[i](x, (self.u_opp['opp_h0_'+str(i)], self.u_opp['opp_c0_'+str(i)]))
            x_opp_all = torch.cat((x_opp_all,x_opp),0)
        x_opp_out = x_opp_all.view(1,1,-1) 
        #General blocks
        x_gen_all, (self.u_gen['gen_h0_0'], self.u_gen['gen_c0_0']) = self.LSTM_gen[0](x, (self.u_gen['gen_h0_0'], self.u_gen['gen_c0_0']))
        for i in range(1,10):
            x_gen, (self.u_gen['gen_h0_'+str(i)], self.u_gen['gen_c0_'+str(i)]) = self.LSTM_gen[i](x, (self.u_gen['gen_h0_'+str(i)], self.u_gen['gen_c0_'+str(i)]))
            #x_gen_all = torch.cat((x_gen_all,self.LSTM_gen[i](x, (i_gen['h0_'+str(i)].view(1,1,10), i_gen['c0_'+str(i)].view(1,1,10)))[0].view(1,1,1,-1)),0)
            x_gen_all = torch.cat((x_gen_all,x_gen),0)
        x_gen_out = x_gen_all.view(1,1,-1)
        
        #Linear layers
        x_lin_h_1 = torch.tanh(self.lin_dec_1(torch.cat((x_gen_out,x_opp_out),2)))
        x_lin_h_2 = torch.tanh(self.lin_dec_2(x_lin_h_1))
        x_out = torch.tanh(self.lin_dec_3(x_lin_h_2))
        return x_out
    
    def reset_u_opp(self):
        self.u_opp = self.i_opp.copy()
    def reset_u_gen(self):
        self.u_gen = self.i_gen.copy()
    def reset(self):
        self.reset_u_opp()
        self.reset_u_gen()
        return
    


class Net_6maxSingle(nn.Module):
    def __init__(self, i_gen):
        super(Net_6maxSingle, self).__init__()
        self.LSTM_gen = []
        for i in range(10):
            self.LSTM_gen.append(nn.LSTM(12, 10))
        self.LSTM_gen = nn.ModuleList(self.LSTM_gen)
        self.lin_dec_1 = nn.Linear(100, 50)
        self.lin_dec_2 = nn.Linear(50, 10)
        self.lin_dec_3 = nn.Linear(10, 1)
        self.i_gen = i_gen
        self.i_opp = dict()
        self.u_gen = i_gen.copy()

    def forward(self, x):        
        #General blocks
        x_gen_all, (self.u_gen['gen_h0_0'], self.u_gen['gen_c0_0']) = self.LSTM_gen[0](x, (self.u_gen['gen_h0_0'], self.u_gen['gen_c0_0']))
        for i in range(1,10):
            x_gen, (self.u_gen['gen_h0_'+str(i)], self.u_gen['gen_c0_'+str(i)]) = self.LSTM_gen[i](x, (self.u_gen['gen_h0_'+str(i)], self.u_gen['gen_c0_'+str(i)]))
            #x_gen_all = torch.cat((x_gen_all,self.LSTM_gen[i](x, (i_gen['h0_'+str(i)].view(1,1,10), i_gen['c0_'+str(i)].view(1,1,10)))[0].view(1,1,1,-1)),0)
            x_gen_all = torch.cat((x_gen_all,x_gen),0)
        x_gen_out = x_gen_all.view(1,1,-1)
        
        #Linear layers
        x_lin_h_1 = torch.tanh(self.lin_dec_1(x_gen_out))
        x_lin_h_2 = torch.tanh(self.lin_dec_2(x_lin_h_1))
        x_out = torch.tanh(self.lin_dec_3(x_lin_h_2))
        return x_out

    def reset_u_gen(self):
        self.u_gen = self.i_gen.copy()
    def reset(self):
        self.reset_u_gen()
        return
    
class Net_6maxFull(nn.Module):
    def __init__(self, i_opp, i_gen):
        super(Net_6maxFull, self).__init__()
        #general blocks
        self.LSTM_gen = []
        for i in range(10):
            self.LSTM_gen.append(nn.LSTM(12, 10))
        self.LSTM_gen = nn.ModuleList(self.LSTM_gen)
        self.lin_dec_1 = nn.Linear(100, 50)
        
        #opponent blocks
        self.nb_players=5
        self.LSTM_opp_round = [0,]*self.nb_players
        self.LSTM_opp_game = [0,]*self.nb_players
        for opponent_id in range(self.nb_opponents):
            for i in range(10):
                self.LSTM_opp.append(nn.LSTM(8, 10))
                self.LSTM_opp = nn.ModuleList(self.LSTM_opp)
            self.lin_dec_1_opp = nn.linear(40,20)
        
        
        self.lin_dec_2 = nn.Linear(70, 10)
        self.lin_dec_3 = nn.Linear(10, 1)
        self.i_opp = i_opp
        self.i_gen = i_gen
        self.u_opp = i_opp.copy()
        self.u_gen = i_gen.copy()


    def forward(self, x):        
        #General blocks
        x_gen=x[:12]
        
        x_gen_all, (self.u_gen['gen_h0_0'], self.u_gen['gen_c0_0']) = self.LSTM_gen[0](x_gen, (self.u_gen['gen_h0_0'], self.u_gen['gen_c0_0']))
        for i in range(1,10):
            x_gen, (self.u_gen['gen_h0_'+str(i)], self.u_gen['gen_c0_'+str(i)]) = self.LSTM_gen[i](x_gen, (self.u_gen['gen_h0_'+str(i)], self.u_gen['gen_c0_'+str(i)]))
            #x_gen_all = torch.cat((x_gen_all,self.LSTM_gen[i](x, (i_gen['h0_'+str(i)].view(1,1,10), i_gen['c0_'+str(i)].view(1,1,10)))[0].view(1,1,1,-1)),0)
            x_gen_all = torch.cat((x_gen_all,x_gen),0)
        x_gen_out = x_gen_all.view(1,1,-1)
        #linear layer
        x_lin_h_1_gen = torch.tanh(self.lin_dec_1(x_gen_out))
        
        #Opponent blocks
        #nb_opps=len(x[12:])/4
        x_opp=torch.Tensor([0,]*5)
        for opp_id in range(5):
            x_opp = x[12+opp_id*5:12+(opp_id+1)*5]
            x_active = x_opp[0]
            x_opp = x_opp[1:]    
            
            x_opp_all, (self.u_opp['opp_h0_0'], self.u_opp['opp_c0_0']) = self.LSTM_opp[0](x, (self.u_opp['opp_h0_0'], self.u_opp['opp_c0_0']))
            for i in range(1,10):
                x_opp, (self.u_opp['opp_h0_'+str(i)], self.u_opp['opp_c0_'+str(i)]) = self.LSTM_opp[i](x, (self.u_opp['opp_h0_'+str(i)], self.u_opp['opp_c0_'+str(i)]))
                x_opp_all = torch.cat((x_opp_all,x_opp),0)
            x_opp_out = x_opp_all.view(1,1,-1) 
            #linear layer
            x_lin_h_1_opp = torch.tanh(self.lin_dec_1_opp(x_opp_out))
            
        x_lin_h_1_opp_avg = np.average()
        
        #final linear layers
        x_lin_h_2 = torch.tanh(self.lin_dec_2(torch.cat((x_lin_h_1_gen,x_lin_h_1_opp),2)))
        x_out = torch.tanh(self.lin_dec_3(x_lin_h_2))
        return x_out

    def reset_u_opp(self):
        self.u_opp = self.i_opp.copy()
    def reset_u_gen(self):
        self.u_gen = self.i_gen.copy()
    def reset(self):
        self.reset_u_opp()
        self.reset_u_gen()
        return
    