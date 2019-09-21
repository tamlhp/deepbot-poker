#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 12:12:27 2019

@author: cyril
"""
import sys
sys.path.append('../redis-server/')

from utils_simul import gen_rand_bots, gen_decks, FakeJob, run_one_game_reg, run_one_game_rebuys, run_one_game_6max_single, run_one_game_6max_full
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
import argparse


if __name__ == '__main__':
    #PARSE ARGUMENTS
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--redis_host',  default='local', type=string, help='Address of redis host. [local, ec2, *]')
    parser.add_argument('--neural_network',  default='6max_full', type=string, help='Neural network architecture to use. [first, second, 6max_single, 6max_full]')
    parser.add_argument('--norm_fitfunc', default=True, type=boolean, help='Wether to use normalization scheme in the genetic algorithm\'s fitness function.')
    parser.add_argument('--worker_timeout', default=800, type=int, help='Time in seconds before a job taken by a worker and not returned is considered to have timed out.')
    parser.add_argument('--simul_id', type=int, help='Id of the simulation. Must be defined to avoid overwriting past simulations.')
    parser.add_argument('--ga_popsize', default=70, type=int, help='Population size of the genetic algorithm.')
    parser.add_argument('--ga_nb_gens', default=250, type=int, help='Number of generations of the genetic algorithm.')
    parser.add_argument('--ga_ini_gen', default=0, type=int, help='The generation at which to start the genetic algorithm. Used to resume an interrupted simulation.')
    parser.add_argument('--max_hands', default=300, type=int, help='Maximum number of hands played in a tournament. If attained, the agent is considered to have lost.')
    parser.add_argument('--small_blind', default=10, type=int, help='Initial small blind amount. If tournament, the blind structure will overrule.')
    parser.add_argument('--ini_stack', default=1500, type=int, help='Initial stack of the players.')
    parser.add_argument('--log_dir', default='./simul_data', type=string, help='The path of the file where the simulation data will be stored.')

    parser.add_argument('--nb_opps', default=4, type=int, help= 'Number of different tables against which to train')


    args = parser.parse_args()
    if args.redis_host == 'local':
        REDIS_HOST = '127.0.0.1'
    elif args.redis_host == 'ec2':
        REDIS_HOST = '172.31.42.99'
    else:
        REDIS_HOST = args.redis_host

    my_network = args.neural_network
    my_normalize = args.norm_fitfunc
    my_timeout = args.worker_timeout
    simul_id = args.simul_id
    nb_bots = args.ga_popsize
    nb_generations = args.ga_nb_gens
    ini_gen = args.ga_ini_gen
    nb_hands = args.max_hands
    sb_amount = args.small_blind
    ini_stack = args.ini_stack

    nb_opps = args.nb_opps #TODO, move to simul arch def
    my_nb_games = nb_opps*4 #TODO, move to simul arch def

    if my_network in ['first','second']: #TODO handle differently.
        my_nb_games=1

    ## Start redis host and clear queue
    redis = Redis(REDIS_HOST)
    q = Queue(connection=redis, default_timeout=my_timeout)
    for j in q.jobs:
        j.cancel()

    ## Neural network layer size reference
    lstm_ref = LSTMBot(network=my_network) #TODO, see if movable

    print('## Starting new simulations ##')

    if ini_gen==0:
        ## Generate first generation of bots (=agents) randomly
        gen_rand_bots(simul_id = simul_id, gen_id=ini_gen, log_dir=log_dir, nb_bots = nb_bots, overwrite=False,
                      network=my_network)

    for gen_id in range(ini_gen, nb_generations):
        print('\n Starting generation: ' + str(gen_id))

        #Define generation's directory. Create except if already existing
        gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
        if not os.path.exists(gen_dir):
            os.makedirs(gen_dir)
        #Empty jobs list
        jobs = []
        #Prepare all decks of the generation
        cst_decks = gen_decks(gen_dir = gen_dir, overwrite=False, nb_hands=nb_hands, nb_games=my_nb_games)
        time_start = time.time()

        for bot_id in range(1,nb_bots+1):
            #Load the bot
            with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:
                lstm_bot_flat = pickle.load(f)
                lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
                lstm_bot = LSTMBot(id_=bot_id, gen_dir = None, full_dict = lstm_bot_dict, network=my_network)
            #Enqueue job to play bot's games
            try:
                jobs.append(q.enqueue(run_games, timeout=my_timeout, kwargs = dict(network=my_network, lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks)))

                if my_network=='6max_single':
                    jobs.append(q.enqueue(run_one_game_6max_single, timeout=my_timeout, kwargs = dict(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks)))
                elif my_network=='6max_full':
                    jobs.append(q.enqueue(run_one_game_6max_full, timeout=my_timeout, kwargs = dict(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks)))
                else:
                    jobs.append(q.enqueue(run_one_game_rebuys, timeout=my_timeout, kwargs = dict(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks)))
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
            time.sleep(1)
            if None not in all_earnings: ###ALL JOBS ARE DONE
                break

            if time.time() - last_enqueue_time > my_timeout:
                print('Reenqueuing unfinished jobs '+ str({sum(x is None for x in all_earnings)}))
                for i in range(len(jobs)):
                    if jobs[i].result is None:
                        try:
                            jobs[i].cancel()
                            if my_network=='6max_single':
                                jobs[i] = q.enqueue(run_one_game_6max_single, kwargs = dict(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks))
                            elif my_network=='6max_full':
                                jobs.append(q.enqueue(run_one_game_6max_full, timeout=my_timeout, result_ttl=my_timeout, kwargs = dict(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks)))
                            else:
                                jobs[i] = q.enqueue(run_one_game_rebuys, kwargs = dict(lstm_bot=lstm_bot, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands, cst_decks = cst_decks))
                        except ConnectionError:
                            print('Currently not connected to redis server')
                            continue
                last_enqueue_time = time.time()
                #print("Number of jobs remaining: " + str(sum([all_earnings[i]==None for i in range(len(all_earnings))])))
            #time.sleep(0.2)

        time_end = time.time()
        print('Done with MATCHES of generation number :'+str(gen_id)+', it took '+str(time_end-time_start) +' seconds.')
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
