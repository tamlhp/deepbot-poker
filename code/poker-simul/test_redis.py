#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 14:13:55 2019

@author: cyril
"""



from redis import Redis
from rq import Queue
import time

q = Queue(connection=Redis())



from test_redis_module import count_words_at_url
result = q.enqueue(
             count_words_at_url, 'http://nvie.com')

time.sleep(2)
print(result.result)