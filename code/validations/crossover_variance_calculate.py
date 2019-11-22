#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 16:38:21 2019

@author: cyril
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 13:02:30 2019

@author: cyril
"""
import pickle
import numpy as np
import matplotlib.pyplot as plt

nb_cards = 52
nb_hands = 500

###CONSTANTS
ga_popsize= 1
simul_id = '-3_cross'
log_dir = '../../../backed_simuls'
sb_amount = 50
ini_stack = 3000
nb_generations = 250
my_network='second'

nb_dif_bots=1000
my_dpi=100

outputs_lstm_1 = []
outputs_lstm_2 = []
outputs_crossover = [[],[],[],[]]
validation_ids=[2,3,4,5]
for gen_id in range(5,nb_dif_bots):
    gen_dir=log_dir+'/simul_'+str(simul_id)+'/gen_'+str(gen_id)
    with open(gen_dir+'/outputs_0.pkl', 'rb') as fr:
        try:
            while True:
                outputs_lstm_1.append(pickle.load(fr))
        except EOFError:
            pass
    with open(gen_dir+'/outputs_1.pkl', 'rb') as fr:
        try:
            while True:
                outputs_lstm_2.append(pickle.load(fr))
        except EOFError:
            pass
    for i, validation_id in enumerate(validation_ids):
        with open(gen_dir+'/outputs_'+str(validation_id)+'.pkl', 'rb') as fr:
            try:
                while True:
                    outputs_crossover[i].append(pickle.load(fr))
            except EOFError:
                pass
            
outputs_lstm_1=np.array(outputs_lstm_1)
outputs_lstm_2=np.array(outputs_lstm_2)
outputs_dif=[0,]*4
outputs_outside=[0,]*4
for i, validation_id in enumerate(validation_ids):
    outputs_crossover[i]=np.array(outputs_crossover[i])
    
    outputs_lstm_dif = np.absolute(outputs_lstm_1-outputs_lstm_2)
    outputs_lstm_mean = np.average([outputs_lstm_1,outputs_lstm_2], axis=0)
    outputs_dif[i]=np.absolute(outputs_crossover[i]-outputs_lstm_mean)
    print('output difference with mean: '+str(np.median(outputs_dif[i])))
    print('output difference with mean, std: '+str(np.std(outputs_dif[i])))
    
    outputs_max = np.max([outputs_lstm_1,outputs_lstm_2],axis=0)
    outputs_min = np.min([outputs_lstm_1,outputs_lstm_2],axis=0)
    dif_min = np.min([np.absolute(outputs_crossover[i]-outputs_lstm_1),np.absolute(outputs_crossover[i]-outputs_lstm_2)],axis=0)
    outputs_outside[i]=np.absolute(np.where(np.logical_and(outputs_crossover[i]<outputs_max, outputs_crossover[i]>outputs_min), 0, dif_min))
    percent_inside = np.sum(np.logical_and(outputs_crossover[i]<outputs_max, outputs_crossover[i]>outputs_min))/len(outputs_crossover[i])
    print('average distance outside bounds: '+str(np.median(outputs_outside[i])))
    print('percent inside: '+str(percent_inside))
    

    print('avg dif between parent outputs: '+str(np.average(outputs_lstm_dif)))
    print('')

parent_dist = np.average(outputs_lstm_dif)/2
plt.plot([0,5],[parent_dist,parent_dist], linewidth='1',color='lightgreen')
plt.boxplot(outputs_dif, 0, '', labels=['per weights','averaged','per group v1','per group v2'], medianprops={'color':'blue'})
plt.legend(['Parents distance'],loc='upper center',bbox_to_anchor=(0.38,1))
plt.xlabel('Crossover method',fontsize='large')
plt.ylabel('Output difference', fontsize='large')
plt.savefig('crossover_change.png',dpi=my_dpi)
plt.clf()

parent_dist = np.average(outputs_lstm_dif)
plt.plot([0,5],[parent_dist,parent_dist], linewidth='1',color='lightgreen')
plt.boxplot(outputs_outside, 0, '', labels=['per weights','averaged','per group v1','per group v2'], medianprops={'color':'blue'})
plt.legend(['Parents distance'],loc='upper center',bbox_to_anchor=(0.38,1))
plt.xlabel('Crossover method',fontsize='large')
plt.ylabel('Output difference', fontsize='large')
plt.savefig('crossover_change_outside.png',dpi=my_dpi)