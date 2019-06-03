#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 12:12:27 2019

@author: cyril
"""
import os
os.environ["OMP_NUM_THREADS"] = "1" # export OMP_NUM_THREADS=4
os.environ["OPENBLAS_NUM_THREADS"] = "1" # export OPENBLAS_NUM_THREADS=4 
os.environ["MKL_NUM_THREADS"] = "1" # export MKL_NUM_THREADS=6
os.environ["VECLIB_MAXIMUM_THREADS"] = "1" # export VECLIB_MAXIMUM_THREADS=4
os.environ["NUMEXPR_NUM_THREADS"] = "1" # export NUMEXPR_NUM_THREADS=6

import ctypes
mkl_rt = ctypes.CDLL('libmkl_rt.so')
mkl_get_max_threads = mkl_rt.mkl_get_max_threads
def mkl_set_num_threads(cores):
    mkl_rt.mkl_set_num_threads(ctypes.byref(ctypes.c_int(cores)))

from utils_simul import gen_rand_bots, gen_decks, run_one_game, compute_ANE, run_all_mp
import pickle
from multiprocessing import Pool
import time

from redis import Redis
from rq import Queue

#from settings_ec2 import REDIS_HOST

"""
if __name__ == '__main__':
    redis = Redis(REDIS_HOST)
    q = Queue(connection=redis)              # start 4 worker processes
    for j in q.jobs:
        j.cancel()
    jobs = []
    time_1 = time.time()
    jobs.append(q.enqueue(run_all_mp, kwargs = dict()))
    time_2 = time.time()
    while True:
        if not(jobs[0].result==None):
            break
        else:
            time.sleep(1)
            print(jobs[0].result)
    print(jobs[0].result)
    print(time_2-time_1)
"""
from settings_ec2 import REDIS_HOST
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
    nb_bots = 12
    nb_hands = 500
    sb_amount = 50
    ini_stack = 20000
    
    ## prepare first gen lstm bots and hands 
    #gen_rand_bots(simul_id = 0,gen_id=0, log_dir=log_dir)
    #gen_decks(simul_id=0,gen_id=0, log_dir=log_dir)
    ## play matches
    with open(gen_dir+'/cst_cheat_ids.pkl', 'rb') as f:  
        cst_cheat_ids = pickle.load(f)
    for bot_id in range(1,nb_bots+1):
        with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'.pkl', 'rb') as f:  
            lstm_bot = pickle.load(f)
        jobs.append(q.enqueue(run_one_game, kwargs = dict(simul_id = 0, gen_id = 0, lstm_bot=lstm_bot, log_dir = log_dir, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_cheat_ids = cst_cheat_ids)))
    
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
        print(earnings)
        with open(gen_dir+'/bots/'+str(i+1)+'/earnings.pkl', 'wb') as f:  
            pickle.dump(earnings, f)

## evolve according to results
#compute_ANE(gen_dir)
    
## prepare second gen lstm bots and hands
    
## play matches