#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 17:16:32 2019

@author: cyril
"""
import mkl
mkl.set_num_threads(1)

import sys
sys.path.append('../PyPokerEngine')
sys.path.append('../redis-server/')
sys.path.append('../poker-simul/')
from pypokerengine.api.game import setup_config, start_poker
from bot_TestBot import TestBot
from bot_CallBot import CallBot
from bot_PStratBot import PStratBot
from bot_LSTMBot import LSTMBot
from bot_EquityBot import EquityBot
from bot_DeepBot import DeepBot #aka Master Bot
from bot_ManiacBot import ManiacBot
from bot_CandidBot import CandidBot
from bot_ConservativeBot import ConservativeBot
import time
import pickle
from utils_simul import gen_decks, gen_rand_bots, run_one_game_rebuys, FakeJob, run_one_game_6max_single, run_one_game_6max_full
from functools import reduce
from neuroevolution import get_full_dict
import random
import numpy as np
from redis import Redis
from rq import Queue


 
machine='ec2'

if machine=='local':
    REDIS_HOST = '127.0.0.1'
elif machine=='ec2':
    REDIS_HOST = '172.31.42.99'

if __name__ == '__main__':      
    ###CONSTANTS
    nb_cards = 52
    nb_hands = 500
    simul_id = -1
    gen_id=-1
    ga_popsize= 1
    log_dir = './simul_data'
    sb_amount = 50
    ini_stack = 3000
    bot_id = 1
    my_timeout = 800
    
    my_network = '6max_full'
    backed_gen_dir = '../../final_agents/simul_13/gen_150'
    
    print('## Starting ##')
    lstm_ref = LSTMBot(None,network=my_network)
    #start redis and clear queue
    redis = Redis(REDIS_HOST)
    q = Queue(connection=redis, default_timeout=my_timeout)   
    for j in q.jobs:
        j.cancel() 
    
    if my_network=='second':
        #all_earnings = []
        jobs = []
        for run_id in range(0,100):
            with open(backed_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:  
                lstm_bot_flat = pickle.load(f)
                lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
                lstm_bot = LSTMBot(id_=bot_id, gen_dir = None, full_dict = lstm_bot_dict, network=my_network)
                
            gen_decks(simul_id=simul_id,gen_id=run_id, log_dir=log_dir,nb_hands = nb_hands)
            gen_dir='./simul_data/simul_'+str(simul_id)+'/gen_'+str(run_id)
            with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
                cst_decks = pickle.load(f)
            cst_decks_match = cst_decks.copy()
            jobs.append(q.enqueue(run_one_game_rebuys, kwargs = dict(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks)))
                                                      
            
        while(True):
            for i in range(len(jobs)):
                if jobs[i].result is not None and not isinstance(jobs[i], FakeJob):
                    jobs[i] = FakeJob(jobs[i])
            all_earnings = [j.result for j in jobs]
            print(all_earnings)
            if None not in all_earnings: ###ALL JOBS ARE DONE
                break
            time.sleep(1)
        
        with open(log_dir+'/simul_'+str(simul_id)+'/bot_earnings.pkl', 'wb') as f:  
            pickle.dump(all_earnings, f)
        
        avg_earning = np.average([list(all_earnings[i].values()) for i in range(len(all_earnings))],axis=0)
        print(avg_earning)
        
    if my_network=='6max_single':
        
        nb_decks = 4
        jobs = []
        for run_id in range(0,250):
            with open(backed_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:  
                lstm_bot_flat = pickle.load(f)
                lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
                lstm_bot = LSTMBot(id_=bot_id, gen_dir = None, full_dict = lstm_bot_dict, network=my_network)
                
            gen_decks(simul_id=simul_id,gen_id=run_id, log_dir=log_dir,nb_hands = nb_hands, nb_decks=nb_decks)
            gen_dir='./simul_data/simul_'+str(simul_id)+'/gen_'+str(run_id)
            with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
                cst_decks = pickle.load(f)
            cst_decks_match = cst_decks.copy()
            jobs.append(q.enqueue(run_one_game_6max_single, kwargs = dict(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks, is_validation=True)))
                                                      
            
        while(True):
            for i in range(len(jobs)):
                if jobs[i].result is not None and not isinstance(jobs[i], FakeJob):
                    jobs[i] = FakeJob(jobs[i])
            all_earnings = [j.result for j in jobs]
            #print(all_earnings)
            if None not in all_earnings: ###ALL JOBS ARE DONE
                break
            print(sum(np.array(all_earnings)==None))
            time.sleep(10)

        
        with open(log_dir+'/simul_'+str(simul_id)+'/bot_earnings.pkl', 'wb') as f:  
            pickle.dump(all_earnings, f)
            
    if my_network=='6max_full':
        
        nb_decks = 16
        jobs = []
        for run_id in range(0,250):
            with open(backed_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:  
                lstm_bot_flat = pickle.load(f)
                lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
                lstm_bot = LSTMBot(id_=bot_id, gen_dir = None, full_dict = lstm_bot_dict, network=my_network)
                
            gen_decks(simul_id=simul_id,gen_id=run_id, log_dir=log_dir,nb_hands = nb_hands, nb_decks=nb_decks)
            gen_dir='./simul_data/simul_'+str(simul_id)+'/gen_'+str(run_id)
            with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
                cst_decks = pickle.load(f)
            cst_decks_match = cst_decks.copy()
            jobs.append(q.enqueue(run_one_game_6max_full, kwargs = dict(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks, is_validation=True)))
                                                      
            
        while(True):
            for i in range(len(jobs)):
                if jobs[i].result is not None and not isinstance(jobs[i], FakeJob):
                    jobs[i] = FakeJob(jobs[i])
            all_earnings = [j.result for j in jobs]
            #print(all_earnings)
            if None not in all_earnings: ###ALL JOBS ARE DONE
                break
            print(sum(np.array(all_earnings)==None))
            time.sleep(10)

        
        with open(log_dir+'/simul_'+str(simul_id)+'/bot_earnings.pkl', 'wb') as f:  
            pickle.dump(all_earnings, f)
        
        #avg_earning = np.average([list(all_earnings[i].values()) for i in range(len(all_earnings))],axis=0)
        #print(avg_earning)

        