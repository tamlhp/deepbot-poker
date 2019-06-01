#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 14:23:22 2019

@author: cyril
"""

import requests

def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())
