#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 12:12:27 2019

@author: cyril
"""
import sys
sys.path.append('../redis-server/')

from utils_simul import gen_rand_bots, gen_decks, FakeJob, run_one_game_reg, run_one_game_rebuys, run_one_game_6max_single
from neuroevolution import select_next_gen_bots, get_best_ANE_earnings, get_full_dict
import pickle
import time
import os

from redis import Redis
from rq import Queue
from neuroevolution import compute_ANE
from bot_LSTMBot import LSTMBot
from utils_io import prep_gen_dirs, get_all_gen_flat
import random
import numpy as np
from operator import add




            #######
            
my_game_mode = '6max'
my_network='6max_single'
my_input_type='pstratstyle'
nb_opps=1
my_normalize=False
my_nb_decks=24

machine='ec2'

if machine=='local':
    REDIS_HOST = '127.0.0.1'
elif machine=='ec2':
    REDIS_HOST = '172.31.42.99'

#redis style
if __name__ == '__main__':
    #start redis and clear queue
    redis = Redis(REDIS_HOST)
    q = Queue(connection=redis)              # start 4 worker processes
    for j in q.jobs:
        j.cancel()
    
    ## layer size references
    lstm_ref = LSTMBot(network=my_network)
    #log dir path
    log_dir = './simul_data'
    simul_id = 9 ## simul id
    

    
    ###CONSTANTS
    nb_bots= 70
    nb_hands = 500
    sb_amount = 10
    ini_stack = 1500
    nb_generations = 250
    nb_sub_matches=10
    
    print('## Starting ##')
    ## prepare first gen lstm bots
    gen_rand_bots(simul_id = simul_id, gen_id=0, log_dir=log_dir, nb_bots = nb_bots, overwrite=False, 
                  network=my_network)
          
    for gen_id in range(275, 300):
        print('\n Starting generation: ' + str(gen_id))
        jobs = []
        #prepare generation deck
        if my_game_mode=='6max':
            gen_decks(simul_id=simul_id,gen_id=gen_id, log_dir=log_dir, overwrite=False, nb_hands=nb_hands, nb_decks=my_nb_decks)            
        else:
            gen_decks(simul_id=simul_id,gen_id=gen_id, log_dir=log_dir, overwrite=False, nb_hands=nb_hands)
        #generation's directory
        gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
        time_1 = time.time()
        ## play matches
        with open(gen_dir+'/cst_decks.pkl', 'rb') as f:  
            cst_decks = pickle.load(f)
        for bot_id in range(1,nb_bots+1):
            with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:  
                lstm_bot_flat = pickle.load(f)
                lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
                lstm_bot = LSTMBot(id_=bot_id, gen_dir = None, full_dict = lstm_bot_dict, 
                                   network=my_network, input_type=my_input_type)
            try:
                if my_game_mode=='6max':
                    jobs.append(q.enqueue(run_one_game_6max_single, kwargs = dict(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks)))
                else:
                    jobs.append(q.enqueue(run_one_game_rebuys, kwargs = dict(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks)))
            except ConnectionError:
                print('Currently not connected to redis server')
                continue
                
        last_enqueue_time = time.time()
        
        
        while True:
            for i in range(len(jobs)):
                if jobs[i].result is not None and not isinstance(jobs[i], FakeJob):
                    #if random.random() < 0.05:
                     #   print(jobs[i].result)
                    jobs[i] = FakeJob(jobs[i])
            
            all_earnings = [j.result for j in jobs]
            if None not in all_earnings: ###ALL JOBS ARE DONE
                break
            
            if time.time() - last_enqueue_time > 180:
                print('Reenqueuing unfinished jobs '+ str({sum(x is None for x in all_earnings)}))
                for i in range(len(jobs)):
                    if jobs[i].result is None:
                        try:
                            jobs[i].cancel()
                            if my_game_mode=='6max':
                                jobs[i] = q.enqueue(run_one_game_6max_single, kwargs = dict(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks))
                            else:
                                jobs[i] = q.enqueue(run_one_game_rebuys, kwargs = dict(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks))
                        except ConnectionError:
                            print('Currently not connected to redis server')
                            continue
                last_enqueue_time = time.time()
                #print("Number of jobs remaining: " + str(sum([all_earnings[i]==None for i in range(len(all_earnings))])))
            #time.sleep(0.2)
        
        time_2 = time.time()
        print('Done with MATCHES of generation number :'+str(gen_id)+', it took '+str(time_2-time_1) +' seconds.')
        ##saving all earnings
        for i, earnings in enumerate(all_earnings):    
            with open(gen_dir+'/bots/'+str(i+1)+'/earnings.pkl', 'wb') as f:  
                pickle.dump(earnings, f)
        
        ## getting best earnings
        best_earnings = get_best_ANE_earnings(all_earnings = all_earnings, BB=2*sb_amount, nb_bots = nb_bots, nb_opps=nb_opps,normalize=my_normalize)
        print('The best agent has the following scores: ' + str(best_earnings))
        #getting average earning of lstm agents
        avg_earnings=[0,]*len(all_earnings[0].values())
        for i in range(nb_bots):
            avg_earnings= list(map(add, avg_earnings, all_earnings[i].values()))
            
        avg_earnings= [el/nb_bots for el in avg_earnings]
        print('The agents won on average: ' +str(avg_earnings))
        with open(gen_dir+'/surv_earnings.pkl', 'wb') as f:  
                pickle.dump(avg_earnings, f)

        ## NEXT GENERATION PREP BOTS
        all_gen_flat = get_all_gen_flat(dir_=gen_dir, nb_bots = nb_bots) # iteration bot infos
        
        next_gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id+1)
        prep_gen_dirs(dir_=next_gen_dir)

        time_3 = time.time()
        next_gen_bots_flat = select_next_gen_bots(log_dir=log_dir, simul_id=simul_id, gen_id=gen_id, all_earnings=all_earnings, BB=2*sb_amount, 
                                                                 nb_bots=nb_bots, all_gen_flat = all_gen_flat, nb_gens = nb_generations,
                                                                 network=my_network, nb_opps=nb_opps, normalize=my_normalize)

                
        """
        gen_bots_job = q.enqueue(select_next_gen_bots, kwargs = dict(log_dir=log_dir, simul_id=simul_id, gen_id=gen_id, all_earnings=all_earnings, BB=2*sb_amount, nb_bots=nb_bots, all_gen_dicts = all_gen_dicts))
        while True:
            if gen_bots_job.result!=None:
                next_gen_bots_dict= gen_bots_job.result
                break
            time.sleep(0.2)
        """
        
        time_4 = time.time()
        print('Done with EVOLUTION of generation number :'+str(gen_id)+', it took '+str(time_4-time_3) +' seconds.')

        
        
        for bot_id in range(1, nb_bots+1):
            #if not os.path.exists(next_gen_dir+'/bots/'+str(bot_id)):
            if not os.path.exists(next_gen_dir+'/bots/'+str(bot_id)):
                os.makedirs(next_gen_dir+'/bots/'+str(bot_id)) 
            lstm_bot_flat = next_gen_bots_flat[bot_id-1]
            with open(next_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'wb') as f:  
                pickle.dump(lstm_bot_flat, f)

