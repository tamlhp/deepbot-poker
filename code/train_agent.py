#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 12:12:27 2019

@author: cyril
"""
import sys
sys.path.append('./redis')
sys.path.append('./bots')
sys.path.append('./main_functions')
sys.path.append('./PyPokerEngine')
import os
import time
import pickle
import argparse
from redis import Redis
from rq import Queue
from operator import add
from u_generate import gen_rand_bots, gen_decks
from u_training_games import run_generation_games
from u_neuroevolution import select_next_gen_bots, get_best_ANE_earnings
from u_formatting import prep_gen_dirs, get_gen_flat_params


if __name__ == '__main__':
    """ #### PARSE ARGUMENTS, AND PROCESS #### """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--simul_id', default = -1, type=int, help='Id of the simulation. Should be defined to avoid overwriting past simulations.')
    parser.add_argument('--redis_host',  default='local', type=str, help='Address of redis host. [local, ec2, *]')
    parser.add_argument('--neural_network',  default='6max_full', type=str, help='Neural network architecture to use. [hu_first, hu_second, 6max_single, 6max_full]')
    parser.add_argument('--norm_fitfunc', default=True, type=bool, help='Wether to use normalization scheme in the genetic algorithm\'s fitness function.')
    parser.add_argument('--worker_timeout', default=800, type=int, help='Time in seconds before a job taken by a worker and not returned is considered to have timed out.')
    parser.add_argument('--ga_popsize', default=8, type=int, help='Population size of the genetic algorithm.')
    parser.add_argument('--ga_nb_gens', default=250, type=int, help='Number of generations of the genetic algorithm.')
    parser.add_argument('--ga_ini_gen', default=0, type=int, help='The generation at which to start the genetic algorithm. Used to resume an interrupted simulation.')
    parser.add_argument('--max_hands', default=300, type=int, help='Maximum number of hands played in a tournament. If attained, the agent is considered to have lost.')
    parser.add_argument('--small_blind', default=10, type=int, help='Initial small blind amount. If tournament, the blind structure will overrule.')
    parser.add_argument('--ini_stack', default=1500, type=int, help='Initial stack of the players.')
    parser.add_argument('--log_dir', default='../data/simul_data', type=str, help='The path of the file where the simulation data will be stored.')
    parser.add_argument('--train_env', default='default', type=str, help='Environment used in training (table size, game type and opponents) [hu_cash_mixed, 6max_sng_ruler, 6max_sng_mixed]')
    parser.add_argument('--verbose', default=True, type= bool, help = 'Whether to print detailled run time information.')
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
    ga_popsize = args.ga_popsize
    nb_generations = args.ga_nb_gens
    ini_gen = args.ga_ini_gen
    nb_hands = args.max_hands
    sb_amount = args.small_blind
    ini_stack = args.ini_stack
    log_dir = args.log_dir
    train_env = args.train_env
    verbose = args.verbose

    nb_opps = args.nb_opps #TODO, move to simul arch def
    my_nb_games = nb_opps*4 #TODO, move to simul arch def

    if my_network in ['hu_first','hu_second']: #TODO handle differently.
        my_nb_games=1

    if train_env == 'default':
        if my_network in ['hu_first','hu_second']:
            train_env = 'hu_cash_mixed'
        elif my_network == '6max_single':
            train_env = '6max_sng_ruler'
        elif my_network =='6max_full':
            train_env = '6max_sng_mixed'

    """ #### SETTING UP #### """

    # Start redis host and clear queue
    redis = Redis(REDIS_HOST)
    q = Queue(connection=redis, default_timeout=my_timeout)
    for j in q.jobs:
        j.cancel()

    if ini_gen==0:
    # if this is a new simulation (not resuming one)
        # Generate the first generation of bots randomly
        gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(ini_gen)
        gen_rand_bots(gen_dir, network=my_network, ga_popsize = ga_popsize, overwrite=False)
        # Write configuration details to text file
        file = open(log_dir+'/simul_'+str(simul_id)+"/configuration_details.txt",'w')
        file.write("## CONFIGURATION DETAILS ## \n \n")
        file.write(str(args))
        file.close()

    """ #### STARTING TRAINING #### """
    if verbose: print('## Starting training session ##')
    for gen_id in range(ini_gen, nb_generations):
        if verbose: print('\n Starting generation: ' + str(gen_id))
        #Define generation's directory. Create one except if already existing
        gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
        if not os.path.exists(gen_dir):
            os.makedirs(gen_dir)
        #Prepare all decks of the generation
        cst_decks = gen_decks(gen_dir = gen_dir, overwrite=False, nb_hands=nb_hands, nb_games=my_nb_games)

        """####  RUN THE GAMES  ####"""
        time_start_games = time.time()
        all_earnings = run_generation_games(gen_dir = gen_dir, ga_popsize = ga_popsize, my_network = my_network,
                                            my_timeout = my_timeout, train_env = train_env, cst_decks=cst_decks,
                                            ini_stack=ini_stack, sb_amount = sb_amount, nb_hands = nb_hands,
                                            q = q)
        # Saving earnings
        for i, earnings in enumerate(all_earnings):
            with open(gen_dir+'/bots/'+str(i+1)+'/earnings.pkl', 'wb') as f:
                pickle.dump(earnings, f)
        if verbose:
            ## Getting best earnings
            best_earnings = get_best_ANE_earnings(all_earnings = all_earnings, BB=2*sb_amount, ga_popsize = ga_popsize, nb_opps=nb_opps,normalize=my_normalize)
            print("Best agent score: {}".format(["%.2f" % earning for earning in best_earnings.values()]))
            # Getting average earning of lstm agents
            avg_earnings=[0,]*len(all_earnings[0].values())
            for i in range(ga_popsize):
                avg_earnings= list(map(add, avg_earnings, all_earnings[i].values()))
            avg_earnings= [el/ga_popsize for el in avg_earnings]
            print("Average agent's scores: {}".format(["%.2f" % earning for earning in avg_earnings]))
        time_end_games = time.time()
        if verbose: print("Running games took {:.0f} seconds.".format(time_end_games-time_start_games))


        """#### EVOLUTION /PREPARE NEXT GENERATION ####"""
        time_start_evo = time.time()
        gen_flat_params = get_gen_flat_params(dir_=gen_dir)
        next_gen_dir = log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id+1)
        prep_gen_dirs(dir_=next_gen_dir)
        next_gen_bots_flat = select_next_gen_bots(log_dir=log_dir, simul_id=simul_id, gen_id=gen_id, all_earnings=all_earnings, BB=2*sb_amount,
                                                                 ga_popsize=ga_popsize, gen_flat_params = gen_flat_params, nb_gens = nb_generations,
                                                                 network=my_network, nb_opps=nb_opps, normalize=my_normalize, verbose = verbose)
        for bot_id in range(1, ga_popsize+1):
            if not os.path.exists(next_gen_dir+'/bots/'+str(bot_id)):
                os.makedirs(next_gen_dir+'/bots/'+str(bot_id))
            lstm_bot_flat = next_gen_bots_flat[bot_id-1]
            with open(next_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'wb') as f:
                pickle.dump(lstm_bot_flat, f)
        time_end_evo = time.time()
        if verbose: print("Evolution took {:.0f} seconds.".format(time_end_evo-time_start_evo))
