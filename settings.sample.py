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
    'rapier': 5,
    'aegis_pick': 5,
    'aegis_deny': 1,
    'aegis_stolen': 1
}

###############################################################################

weights = {
    'duration': 1,
    'kills_total': 1,
    'kills_difference': 1,
    'advantage_flips_gold': 2,
    'advantage_flips_experience': 2,
    'team_rating_average': 1,
    'team_rating_difference': 1,
    'non_meta_picks': 1,
    'aegis_pick': 2,
    'aegis_deny': 2,
    'aegis_stolen': 2,
    'rapier_pick': 1.5,
    'rapier_drop': 1,
    'teamfights': 1,
    'gold_per_min': 0.75,
    'xp_per_min': 0.75,
    'last_hits_per_min': 0.75,
    'surprise_factor': 1
}

###############################################################################
