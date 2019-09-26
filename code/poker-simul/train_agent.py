#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 12:12:27 2019

@author: cyril
"""
import sys
sys.path.append('../redis-server/')

from u_generate import gen_rand_bots, gen_decks
from u_run_games import run_games, FakeJob
from u_neuroevolution import select_next_gen_bots, get_best_ANE_earnings, get_full_dict
from u_store_bots import get_full_dict, prep_gen_dirs, get_gen_flat_params
import pickle
import time
import os

from redis import Redis
from rq import Queue
from neuroevolution import compute_ANE
from bot_LSTMBot import LSTMBot
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
    parser.add_argument('--train_env', default='default', type=string, help='Environment used in training (table size, game type and opponents) [hu_cash_mixed, 6max_sng_ruler, 6max_sng_mixed]')
    paser.add_argument('--verbose', default=True, type= boolean, help = 'Whether to print detailled run time information.')

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
    train_env = args.train_env
    verbose = args.verbose

    nb_opps = args.nb_opps #TODO, move to simul arch def
    my_nb_games = nb_opps*4 #TODO, move to simul arch def

    if my_network in ['first','second']: #TODO handle differently.
        my_nb_games=1

    if train_env == 'default':
        if my_network in ['first','second']:
            train_env = 'hu_cash_mixed'
        elif my_network == '6max_single':
            train_env = '6max_sng_ruler'
        elif my_network =='6max_full':
            train_env = '6max_sng_mixed'

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
        if verbose:
            print('\n Starting generation: ' + str(gen_id)
        #Define generation's directory. Create except if already existing
        gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
        if not os.path.exists(gen_dir):
            os.makedirs(gen_dir)
        #Empty jobs list
        jobs = []
        #Prepare all decks of the generation
        cst_decks = gen_decks(gen_dir = gen_dir, overwrite=False, nb_hands=nb_hands, nb_games=my_nb_games)

        """####  RUN THE GAMES  ####"""
        time_start_games = time.time()
        #all_earnings = run_generation_games()
        for bot_id in range(1,nb_bots+1):
            #Load the bot
            with open(gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:
                lstm_bot_flat = pickle.load(f)
                lstm_bot_dict = get_full_dict(all_params = lstm_bot_flat, m_sizes_ref = lstm_ref)
                lstm_bot = LSTMBot(id_=bot_id, gen_dir = None, full_dict = lstm_bot_dict, network=my_network)
            #Enqueue job to play bot's games
            try:
                jobs.append(q.enqueue(run_games, timeout=my_timeout, kwargs = dict(train_env=train_env, lstm_bot=lstm_bot, cst_decks = cst_decks, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands)))
            except ConnectionError:
                print('Currently not connected to redis server')
                continue

        last_enqueue_time = time.time()
        # Fetch jobs' statusses every second
        while True:
            for i in range(len(jobs)):
                if jobs[i].result is not None and not isinstance(jobs[i], FakeJob):
                    jobs[i] = FakeJob(jobs[i])
            all_earnings = [j.result for j in jobs]
            time.sleep(1) #1 second
            # If all jobs are done, break
            if None not in all_earnings:
                break
            # If jobs are not finished after timeout threshold, reenqueue.
            # Helps when connection occasionaly breaks. May also be the sign of an error in u_run_games.py.
            if time.time() - last_enqueue_time > my_timeout:
                print('Reenqueuing unfinished jobs '+ str({sum(x is None for x in all_earnings)}))
                for i in range(len(jobs)):
                    if jobs[i].result is None:
                        try:
                            jobs[i].cancel()
                            jobs.append(q.enqueue(run_games, timeout=my_timeout, kwargs = dict(train_env=train_env, lstm_bot=lstm_bot, cst_decks = cst_decks, ini_stack = ini_stack, sb_amount=sb_amount, nb_hands = nb_hands)))
                        except ConnectionError:
                            print('Currently not connected to redis server')
                            continue
                last_enqueue_time = time.time()
                #if verbose:
                    #print("Number of jobs remaining: " + str(sum([all_earnings[i]==None for i in range(len(all_earnings))])))
        # Saving earnings
        for i, earnings in enumerate(all_earnings):
            with open(gen_dir+'/bots/'+str(i+1)+'/earnings.pkl', 'wb') as f:
                pickle.dump(earnings, f)
        if verbose:
            ## Getting best earnings
            best_earnings = get_best_ANE_earnings(all_earnings = all_earnings, BB=2*sb_amount, nb_bots = nb_bots, nb_opps=nb_opps,normalize=my_normalize)
            print('The best agent has the following scores: ' + str(best_earnings))
            # Getting average earning of lstm agents
            avg_earnings=[0,]*len(all_earnings[0].values())
            for i in range(nb_bots):
                avg_earnings= list(map(add, avg_earnings, all_earnings[i].values()))
            avg_earnings= [el/nb_bots for el in avg_earnings]
            print('The agents won on average: ' +str(avg_earnings))
        time_end_games = time.time()
        if verbose: print('Running games took '+str(time_end_games-time_start_games) +' seconds.')


        """####  PREPARE NEXT GENERATION / EVOLUTION ####"""
        time_start_evo = time.time()
        gen_flat_params = get_gen_flat_params(dir_=gen_dir, nb_bots=nb_bots)
        next_gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id+1)
        prep_gen_dirs(dir_=next_gen_dir)
        next_gen_bots_flat = select_next_gen_bots(log_dir=log_dir, simul_id=simul_id, gen_id=gen_id, all_earnings=all_earnings, BB=2*sb_amount,
                                                                 nb_bots=nb_bots, gen_flat_params = gen_flat_params, nb_gens = nb_generations,
                                                                 network=my_network, nb_opps=nb_opps, normalize=my_normalize, verbose = verbose)
        for bot_id in range(1, nb_bots+1):
            if not os.path.exists(next_gen_dir+'/bots/'+str(bot_id)):
                os.makedirs(next_gen_dir+'/bots/'+str(bot_id))
            lstm_bot_flat = next_gen_bots_flat[bot_id-1]
            with open(next_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'wb') as f:
                pickle.dump(lstm_bot_flat, f)
        time_end_evo = time.time()
        if verbose: print('Evolution took '+str(time_end_evo-time_start_evo) +' seconds.')
