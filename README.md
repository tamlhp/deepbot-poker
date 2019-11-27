# Deepbot

This project implements a bot playing No Limit Texas Hold'em poker. It has been trained to play Heads Up Ring Game, or 6 Handed Sit and Go. The model is a neural network trained with a genetic algorithm. The detailed report can be found in ./docs/final-report.

## Setting up
As a lot of data is generated during training, not everything is included in this repository. To keep it ordered, this repository should be clone inside another repository, for example Deepbot_local:
```
mkdir Deepbot_local
cd Deepbot_local
git clone https://github.com/tamlhp/deepbot.git --recursive
```
Note that the recursive arguments is used as their are two submodules in this repository: PyPokerEngine is used to simulate games locally and OMPEval is used to estimate the equity of a hand.

Apart from the github repository, another folder called backed_simuls maintains the data generated from training. This data includes all agents that appeared during the neuroevolution as well as the decks used. This way the training can be reproduced, or restarted from any given point. To bring the trained agents' data into backed_simuls, run the initialization script:
```
cd Deepbot
sh init_script.sh
```

## Make a trained agent play
An agent is saved as a single list containing all the trainable parameters of its neural network. The code below is a simple way to load an agent. An example of the usage of this code to play a game can be found in ./code/poker-simul/verify_a_bot.py
```
my_network = '6max_full'  #The neural network used
simul_id = 13             #The training instance
train_gen_id = 250        #The generation of the agent picked (the latest here)
bot_id = 1                #The first agent, thus the best of the last generation
backed_gen_dir = '../../../backed_simuls/simul_'+str(simul_id)+'/gen_'+str(train_gen_id)
#Used for reference of the size of the layers
ref_full_dict = DeepBot(network=my_network).full_dict
with open(backed_gen_dir+'/bots/'+str(bot_id)+'/bot_'+str(bot_id)+'_flat.pkl', 'rb') as f:
    #The trainable parameters in a single list
    deepbot_flat = pickle.load(f)
    #The trainable parameters in a dictionary separating by layer
    deepbot_dict = get_full_dict(all_params = deepbot_flat, ref_full_dict = ref_full_dict)
    #The actual bot, compatible with PyPokerEngine
    deepbot = DeepBot(id_ = bot_id, gen_dir = '.', full_dict = deepbot_dict, network=my_network)
```
There are three trained agents:
- Simulation 8: Plays Heads Up Ring Game against various opponents
- Simulation 9: Plays 6 Handed Sit and Go against the Ruler
- Simulation 13: Plays 6 Handed Sit and Go against various opponents

## Training an agent
Everything in this section is done within ./code/poker-simul
To train an agent from scratch, the script simulate_games.py is to be used. As a lot of games have to be played, redis is used to enable cloud computing. To run locally simply run:
```
redis-server&
sh run_workers.sh 70 local&
python3 simulate_games.py
```
The first argument of run_workers.sh defines the number of workers to run. 70 is ideal as it is the size of the population. However, this value should be put to the number of threads available on the machine minus 1, for efficient multi-threading.

To run in the cloud, the ip address of the host (ec2) as to be changed. This is in simulate_games.py, worker_script.py and redis_ec2.conf. In addition in simulate_games.py the variable 'machine' has to be set to 'ec2'
On the host machine run:
```
redis-server redis_ec2.conf
```
On the cloud computing machine run:
```
sh run_workers.sh 70 ec2
```
Back on the host machine run:
```
python3 simulate_games.py
```
The host will send games to be simulated to the computing machine, which will return the performance of the agent at these games. This is done for 250 generations.


## start gui
pypokergui serve /home/cyril/Documents/deepbot/deepbot-git/code/poker-simul/poker_conf.yaml --port 8000 --speed moderate
