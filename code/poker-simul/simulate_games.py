#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 12:12:27 2019

@author: cyril
"""

from utils_simul import gen_rand_bots, gen_decks, run_one_game
from neuroevolution import select_next_gen_bots, get_best_ANE_earnings
import pickle
import time
import os

from redis import Redis
from rq import Queue
from neuroevolution import compute_ANE
from bot_LSTMBot import LSTMBot
from utils_io import prep_gen_dirs, get_all_gen_dicts

from settings_ec2 import REDIS_HOST
#redis style
if __name__ == '__main__':
    #start redis and clear queue
    redis = Redis(REDIS_HOST)
    q = Queue(connection=redis)              # start 4 worker processes
    for j in q.jobs:
        j.cancel()
    
    #log dir path
    log_dir = './simul_data'
    simul_id = 0 ## simul id
    
    ## prepare first gen lstm bots
    gen_rand_bots(simul_id = 0, gen_id=0, log_dir=log_dir)
    
    ###CONSTANTS
    nb_bots= 50
    nb_hands = 500
    sb_amount = 50
    ini_stack = 20000
    nb_generations = 250
    print('## Starting ##')
    for gen_id in range(nb_generations):
        jobs = []
        #prepare generation deck
        gen_decks(simul_id=simul_id,gen_id=gen_id, log_dir=log_dir)
        #generation's directory
        gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
        time_1 = time.time()
        ## play matches
        with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
            cst_decks = pickle.load(f)
        for bot_id in range(1,nb_bots+1):
            with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_dict.pkl', 'rb') as f:  
                lstm_bot_dict = pickle.load(f)
                lstm_bot = LSTMBot(id_=bot_id, gen_dir = None, full_dict = lstm_bot_dict)
            jobs.append(q.enqueue(run_one_game, kwargs = dict(simul_id = 0, gen_id = 0, lstm_bot=lstm_bot, log_dir = log_dir, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks)))
        
        while True:
            all_earnings = [j.result for j in jobs]
            if None not in all_earnings:
                break
            else:
                pass
                #print("Number of jobs remaining: " + str(sum([all_earnings[i]==None for i in range(len(all_earnings))])))
            time.sleep(0.2)
        
        time_2 = time.time()
        print('Done with MATCHES of generation number :'+str(gen_id)+', it took '+str(time_2-time_1) +' seconds.')
        best_earnings = get_best_ANE_earnings(all_earnings = all_earnings, BB=2*sb_amount)
        print('The best agent has the following scores: ' + str(best_earnings))
        
        for i, earnings in enumerate(all_earnings):    
            with open(gen_dir+'/bots/'+str(i+1)+'/earnings.pkl', 'wb') as f:  
                pickle.dump(earnings, f)
                

        ## NEXT GENERATION PREP BOTS
        all_gen_dicts = get_all_gen_dicts(dir_=gen_dir, nb_bots = nb_bots) # iteration bot infos
        
        next_gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id+1)
        prep_gen_dirs(dir_=next_gen_dir)

        time_3 = time.time()
        #next_gen_bots_dict = select_next_gen_bots(log_dir=log_dir, simul_id=simul_id, gen_id=gen_id, all_earnings=all_earnings, BB=2*sb_amount, nb_bots=nb_bots, all_gen_dicts = all_gen_dicts)
        gen_bots_job = q.enqueue(select_next_gen_bots, kwargs = dict(log_dir=log_dir, simul_id=simul_id, gen_id=gen_id, all_earnings=all_earnings, BB=2*sb_amount, nb_bots=nb_bots, all_gen_dicts = all_gen_dicts))
        while True:
            if gen_bots_job.result!=None:
                next_gen_bots_dict= gen_bots_job.result
                break
            time.sleep(0.2)
                
        time_4 = time.time()
        print('Done with EVOLUTION of generation number :'+str(gen_id)+', it took '+str(time_4-time_3) +' seconds.')

        
        
        for bot_id in range(1, nb_bots+1):
            #if not os.path.exists(next_gen_dir+'/bots/'+str(bot_id)):
            os.makedirs(next_gen_dir+'/bots/'+str(bot_id)) 
            lstm_bot_dict = next_gen_bots_dict[bot_id-1]
            with open(next_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_dict.pkl', 'wb') as f:  
                pickle.dump(lstm_bot_dict, f)

