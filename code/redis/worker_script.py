#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 03:07:21 2019
@author: cyril
"""

#!/usr/bin/env python
import sys
from rq import Connection, Worker
from redis import Redis

import mkl
mkl.set_num_threads(1)
# Preload libraries

import sys
sys.path.append('../bots/')
sys.path.append('../PyPokerEngine/')
sys.path.append('../poker-simul/')
from pypokerengine.api.game import setup_config, start_poker
from bot_CallBot import CallBot
from bot_ConservativeBot import ConservativeBot
from bot_ManiacBot import ManiacBot
from bot_PStratBot import PStratBot
from bot_LSTMBot import LSTMBot
from bot_CandidBot import CandidBot
from bot_EquityBot import EquityBot
import random
import pickle
import numpy as np
import time
from multiprocessing import Pool
import os
from functools import reduce
from collections import OrderedDict
from u_formatting import get_flat_params


#setting up connection
machine = sys.argv[1]
if machine=='local':
    REDIS_HOST = '127.0.0.1'
elif machine=='ec2':
    REDIS_HOST = '172.31.42.99'

conn1 = Redis(REDIS_HOST, 6379)

with Connection():
    #qs = ['default']

    w = Worker('default', connection=conn1)
    w.work()
