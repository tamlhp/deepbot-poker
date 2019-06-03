#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 16:01:21 2019

@author: cyril
"""

import mkl
mkl.set_num_threads(1)
import torch
import pandas as pd

def load_data(hands_csv):    
    
    #torch.set_default_tensor_type('torch.FloatTensor')

    
    with open(hands_csv, 'r') as hand_data_csv:
        df_hands = pd.read_csv(hand_data_csv)
        
    # Randomly sample 80% as training
    df_training = df_hands.sample(frac=0.8)
    # And 20% as testing
    df_testing = df_hands.loc[~df_hands.index.isin(df_training.index)]
        
    df_train_input = df_training.iloc[:, 1:-1]    
    df_train_target = df_training.iloc[:,-1]
    
    df_test_input = df_testing.iloc[:, 1:-1]
    df_test_target = df_testing.iloc[:,-1]
    
    #normalize input
    df_train_input = (df_train_input-df_train_input.mean())/df_train_input.std()
    df_test_input = (df_test_input-df_train_input.mean())/df_train_input.std()
    
    #turn to torch tensor
    train_input = torch.FloatTensor(df_train_input.values)
    train_target = torch.FloatTensor(df_train_target.values)
    test_input = torch.FloatTensor(df_test_input.values)
    test_target = torch.FloatTensor(df_test_target.values)
    
    return train_input, train_target, test_input, test_target
    