#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 14:43:26 2019

@author: cyril
"""

#from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
#import argpars
import torch
from torch.autograd import Variable
from torch import nn
from torch.nn import functional as F
from torch import FloatTensor as Tensor



from data_loader import load_data

################################
# parse inputs # 
################################
"""
parser = argparse.ArgumentParser(description='Train a conv net to predict state value')

parser.add_argument('--hands-csv-path',  type=str, default= '../../data/hand-data/', help='path of csvs containing hand data')
parser.add_argument('--precomputed-inputs', type =bool, default=True, help='Use the precomputed NN inputs as present in the csv path')
parser.add_argument('--MC-simulations',  type=int, default=100 , help='Number of monte-carlo simulations for equity estimation. \
                                                                        Only has effect if precomputed_inputs == False')


args = parser.parse_args()
#params
mc_simulations = args.MC_simulations
hand_data = args.hands_csv
"""


torch.set_default_tensor_type('torch.cuda.FloatTensor')

##load data
train_input, train_target, test_input, test_target = load_data('../../data/hand-data/'+'features.csv')


### Use cuda if available
if torch.cuda.is_available():
    print('Cuda is available :)')
    train_input, train_target = train_input.cuda(), train_target.cuda()
    test_input, test_target = test_input.cuda(), test_target.cuda()
    device = torch.device('cuda')
else:
    print('Cuda is not available :(')
    device = torch.device('cpu')

################################
# define network #
################################

input_size = 14
nb_hidden_1 = 32
nb_hidden_2 = 8

class Net1(nn.Module):
    def __init__(self, input_size, nb_hidden_1, nb_hidden_2):
        super(Net1, self).__init__()
        self.fc1 = nn.Linear(input_size, nb_hidden_1)
        self.fc2 = nn.Linear(nb_hidden_1, nb_hidden_2)
        self.fc3 = nn.Linear(nb_hidden_2, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x
    
    
################################
# train the network #
################################    
    
    

def train_model(model, train_input, train_target, mini_batch_size):
    criterion = nn.MSELoss()
    eta = 1e-1

    for iter_ in range(25):
        sum_loss = 0
        for b in range(0, train_input.size(0), mini_batch_size):
            if b+mini_batch_size > train_input.size(0):
                continue
            output = model(train_input.narrow(0, b, mini_batch_size))
            loss = criterion(output, train_target.narrow(0, b, mini_batch_size))
            model.zero_grad()
            loss.backward()
            sum_loss = sum_loss + loss.item()
            with torch.no_grad():
                for p in model.parameters():
                    p -= eta * p.grad
        print(iter_, sum_loss)
        
        
def compute_nb_errors(model, input, target, mini_batch_size):
    avg_error = 0

    for b in range(0, input.size(0)-mini_batch_size, mini_batch_size):
        output = model(input.narrow(0, b, mini_batch_size))
        for k in range(mini_batch_size):
            #print(target[b+k])
            #print(output)
            avg_error = avg_error+ abs(target[b+k] - output)
    #print(output)
    return avg_error



#### MAIN #####
mini_batch_size =500

print(train_input.narrow(0, 500, 1000).size())
    
model = Net1(input_size, nb_hidden_1, nb_hidden_2).to(device=device)
train_model(model, train_input, train_target, mini_batch_size)
avg_error = compute_nb_errors(model, test_input, test_target, mini_batch_size)
#print('test average error Net: '+ str(avg_error))