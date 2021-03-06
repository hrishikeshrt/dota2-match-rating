#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 18:27:25 2021

@author: Hrishikesh Terdalkar
"""

import re
import requests
from bs4 import BeautifulSoup

###############################################################################


def extract_match_ids(url):
    """
    Extract Match IDs from URL

    Match IDs are extracted from their datdota/dotabuff/stratz links
    """
    html = requests.get(url).content.decode()
    soup = BeautifulSoup(html, 'lxml')
    all_links = [a['href'] for a in soup.find_all('a') if 'href' in a.attrs]
    patterns = [
        'datdota.com/matches/([0-9]+)$',
        'dotabuff.com/matches/(0-9]+)$',
        'stratz.com/en-us/match/([0-9]+)$'
    ]

    match_ids = []
    for link in all_links:
        for pattern in patterns:
            m = re.search(pattern, link)
            if m:
                match_ids.append(m.group(1))

    return list(set(match_ids))

###############################################################################
