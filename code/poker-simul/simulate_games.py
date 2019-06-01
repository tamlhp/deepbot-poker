#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 12:12:27 2019

@author: cyril
"""

from utils_simul import gen_rand_bots, gen_decks, run_one_game, compute_ANE
import pickle
from multiprocessing import Pool
import time

from redis import Redis
from rq import Queue
##multiproc style
"""
if __name__ == '__main__':
    time_1 = time.time()
    pool = Pool(processes=1)              # start 4 worker processes
    
    log_dir = './simul_data'
    simul_id = 0 ## simul id
    gen_id = 0 ## gen id
    gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    nb_bots = 8
    nb_hands = 50
    sb_amount = 50
    ini_stack = 20000
    
    ## prepare first gen lstm bots and hands 
    gen_rand_bots(simul_id = 0,gen_id=0, log_dir=log_dir)
    gen_decks(simul_id=0,gen_id=0, log_dir=log_dir)
    ## play matches
    for bot_id in range(1,nb_bots+1):
        with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'.pkl', 'rb') as f:  
            lstm_bot = pickle.load(f)
        pool.apply_async(run_one_game,(), dict(simul_id = 0, gen_id = 0, lstm_bot=lstm_bot, log_dir = log_dir, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands))
    pool.close()
    pool.join()
    time_2 = time.time()
    
    print(time_2-time_1)
"""
from settings import REDIS_HOST
#redis style
if __name__ == '__main__':
    time_1 = time.time()
    redis = Redis(REDIS_HOST)
    q = Queue(connection=redis)              # start 4 worker processes
    for j in q.jobs:
        j.cancel()
    jobs = []
    
    log_dir = './simul_data'
    simul_id = 0 ## simul id
    gen_id = 0 ## gen id
    gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    nb_bots = 8
    nb_hands = 100
    sb_amount = 50
    ini_stack = 20000
    
    ## prepare first gen lstm bots and hands 
    gen_rand_bots(simul_id = 0,gen_id=0, log_dir=log_dir)
    gen_decks(simul_id=0,gen_id=0, log_dir=log_dir)
    ## play matches
    for bot_id in range(1,nb_bots+1):
        with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'.pkl', 'rb') as f:  
            lstm_bot = pickle.load(f)
        jobs.append(q.enqueue(run_one_game, kwargs = dict(simul_id = 0, gen_id = 0, lstm_bot=lstm_bot, log_dir = log_dir, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands)))
    
    while True:
        scores = [j.result for j in jobs]
        if None not in scores:
            break
        else:
            print("Number of jobs remaining: " + str(sum([scores[i]==None for i in range(len(scores))])))
        time.sleep(1)
    
    time_2 = time.time()
    print(time_2-time_1)

    for i, earnings in enumerate(scores):    
        with open(gen_dir+'/bots/'+str(i+1)+'/earnings.pkl', 'wb') as f:  
            pickle.dump(earnings, f)
## evolve according to results
#compute_ANE(gen_dir)
    
## prepare second gen lstm bots and hands
    
## play matches