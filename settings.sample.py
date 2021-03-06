#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 06 18:33:33 2021

@author: Hrishikesh Terdalkar
"""

import os

###############################################################################

home_dir = os.path.expanduser('~')
data_dir = os.path.join(home_dir, 'dota2')

###############################################################################

normalizers = {
    'duration': 3600,
    'kills': 100,
    'teamfights': 10,
    'tier': {
        'premium': 1,
        'professional': 0.75
    },
    'rapier': 2,
    'aegis_pick': 3,
    'aegis_deny': 1,
    'aegis_stolen': 1
}

###############################################################################

league_urls = {
    'dpc_eu_1_upper': 'https://liquipedia.net/dota2/Dota_Pro_Circuit/2021/1/Europe/Upper_Division'
}

###############################################################################
