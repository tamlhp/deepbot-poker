#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 19:34:51 2019

@author: cyril
"""
from torch import nn
import torch
import numpy as np

class Net_HuFirst(nn.Module):
    def __init__(self, i_opp, i_gen):
        super(Net_HuFirst, self).__init__()
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
        x_opp_out = self.LSTM_opp(x)
        x_gen_all, (self.u_gen['gen_h0_0'], self.u_gen['gen_c0_0']) = self.LSTM_gen[0](x, (self.u_gen['gen_h0_0'], self.u_gen['gen_c0_0']))
        for i in range(1,10):
            x_gen, (self.u_gen['gen_h0_'+str(i)], self.u_gen['gen_c0_'+str(i)]) = self.LSTM_gen[i](x, (self.u_gen['gen_h0_'+str(i)], self.u_gen['gen_c0_'+str(i)]))
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



class Net_HuSecond(nn.Module):
    def __init__(self, i_opp, i_gen):
        super(Net_HuSecond, self).__init__()
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
        #self.lin_dec_1 = nn.Linear(100, 50)

        #opponent blocks
        self.LSTM_opp_round = []
        self.LSTM_opp_game = []
        for i in range(10):
            self.LSTM_opp_round.append(nn.LSTM(4, 5))
        self.LSTM_opp_round = nn.ModuleList(self.LSTM_opp_round)
        for i in range(10):
            self.LSTM_opp_game.append(nn.LSTM(4, 5))
        self.LSTM_opp_game = nn.ModuleList(self.LSTM_opp_game)

        self.LSTM_opp_round=nn.ModuleList(self.LSTM_opp_round)
        self.LSTM_opp_game=nn.ModuleList(self.LSTM_opp_game)

        self.lin_dec_1 = nn.Linear(200,50)
        self.lin_dec_2 = nn.Linear(50, 10)
        self.lin_dec_3 = nn.Linear(10, 1)
        self.i_opp = i_opp
        self.i_gen = i_gen
        self.u_opp = i_opp.copy()
        self.u_gen = i_gen.copy()
        self.nb_opponents=5
        #print(self.u_gen.keys())

    def forward(self, x):
        #General blocks (game relative)
        x_gen_in=x[:,:,:12]
        x_gen_all, (self.u_gen['gen_h0_0'], self.u_gen['gen_c0_0']) = self.LSTM_gen[0](x_gen_in, (self.u_gen['gen_h0_0'], self.u_gen['gen_c0_0']))
        for i in range(1,10):
            x_gen, (self.u_gen['gen_h0_'+str(i)], self.u_gen['gen_c0_'+str(i)]) = self.LSTM_gen[i](x_gen_in, (self.u_gen['gen_h0_'+str(i)], self.u_gen['gen_c0_'+str(i)]))
            x_gen_all = torch.cat((x_gen_all,x_gen),0)
        x_gen_out = x_gen_all.view(1,1,-1)

        #Opponent blocks
        x_opp_out=[]
        for opp_id in range(self.nb_opponents):
            #take inputs correspoding to opponent
            x_opp = x[:,:,12+opp_id*5:12+(opp_id+1)*5]
            x_active = x_opp[:,:,0]
            x_opp_in = x_opp[:,:,1:]

            ##opponent game relative lstms
            x_opp_single, (self.u_gen['opp_game_h0_'+str(opp_id)+'_0'], self.u_gen['opp_game_c0_'+str(opp_id)+'_0']) = self.LSTM_opp_game[0](x_opp_in, (self.u_gen['opp_game_h0_'+str(opp_id)+'_0'], self.u_gen['opp_game_c0_'+str(opp_id)+'_0']))
            for i in range(1,10):
                x_opp_game, (self.u_gen['opp_game_h0_'+str(opp_id)+'_'+str(i)], self.u_gen['opp_game_c0_'+str(opp_id)+'_'+str(i)]) = self.LSTM_opp_game[i](x_opp_in, (self.u_gen['opp_game_h0_'+str(opp_id)+'_'+str(i)], self.u_gen['opp_game_c0_'+str(opp_id)+'_'+str(i)]))
                x_opp_single = torch.cat((x_opp_single,x_opp_game),0)
            #opponent round relative lstms
            for i in range(0,10):
                x_opp_round, (self.u_opp['opp_round_h0_'+str(opp_id)+'_'+str(i)], self.u_opp['opp_round_c0_'+str(opp_id)+'_'+str(i)]) = self.LSTM_opp_round[i](x_opp_in, (self.u_opp['opp_round_h0_'+str(opp_id)+'_'+str(i)], self.u_opp['opp_round_c0_'+str(opp_id)+'_'+str(i)]))
                x_opp_single = torch.cat((x_opp_single,x_opp_game),0)

            x_opp_single = x_opp_single.view(1,1,-1)
            #keep in list if player is active
            if int(x_active)==1:
                x_opp_out.append(x_opp_single)

        #Average of active opponent outputs
        if len(x_opp_out)!=0:
            x_opp_out_avg = torch.stack(x_opp_out).mean(0)
        else:
            print('[Warning] From networks.py; No opponents!')
            x_opp_out_avg = torch.zeros([1,1,100])
        #final linear layers
        x_lin_h_1 = torch.tanh(self.lin_dec_1(torch.cat((x_gen_out,x_opp_out_avg),2)))
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
