#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 12:12:27 2019

@author: cyril
"""

from utils_simul import gen_rand_bots, gen_decks, run_one_game, compute_ANE, select_next_gen_bots
import pickle
import time

from redis import Redis
from rq import Queue


from settings import REDIS_HOST
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
    nb_bots = 4
    nb_hands = 100
    sb_amount = 500
    ini_stack = 20000
    nb_generations = 250
    
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
            with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'.pkl', 'rb') as f:  
                lstm_bot = pickle.load(f)
            jobs.append(q.enqueue(run_one_game, kwargs = dict(simul_id = 0, gen_id = 0, lstm_bot=lstm_bot, log_dir = log_dir, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks)))
        
        while True:
            all_earnings = [j.result for j in jobs]
            if None not in all_earnings:
                break
            else:
                print("Number of jobs remaining: " + str(sum([all_earnings[i]==None for i in range(len(all_earnings))])))
            time.sleep(1)
        
        time_2 = time.time()
        print('Done with generation number :'+str(gen_id)+', it took '+str(time_2-time_1) +' seconds.')
        print(all_earnings)
        
        for i, earnings in enumerate(all_earnings):    
            with open(gen_dir+'/bots/'+str(i+1)+'/earnings.pkl', 'wb') as f:  
                pickle.dump(earnings, f)
                
                
        ## NEXT GENERATION PREP BOTS
        next_gen_bots = select_next_gen_bots(log_dir=log_dir, simul_id=simul_id, gen_id=gen_id, all_earnings=all_earnings, BB=2*sb_amount, nb_bots=nb_bots)
        for bot_id in range(1, nb_bots+1): 
            lstm_bot = next_gen_bots[bot_id-1]
            with open(log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id+1)+'/bots/'+str(lstm_bot.id)+'/bot_'+str(lstm_bot.id)+'.pkl', 'wb') as f:  
                    pickle.dump(lstm_bot, f)
            