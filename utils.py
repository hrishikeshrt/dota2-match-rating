#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility Functions
"""

import re

import requests
from bs4 import BeautifulSoup

###############################################################################


def extract_match_id(url):
    """Extract Match ID from Match URL (datdota/dotabuff/stratz)"""
    patterns = [
        'opendota.com/matches/([0-9]+)$',
        'datdota.com/matches/([0-9]+)$',
        'dotabuff.com/matches/(0-9]+)$',
        'stratz.com/en-us/match/([0-9]+)$'
    ]

    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return None


def extract_all_match_ids(league_url):
    """Extract Match IDs from League URL"""
    html = requests.get(league_url).content.decode()
    soup = BeautifulSoup(html, 'lxml')
    all_links = [a['href'] for a in soup.find_all('a') if 'href' in a.attrs]
    match_ids = []
    for link in all_links:
        match_id = extract_match_id(link)
        if match_id is not None:
            match_ids.append(match_id)

    return list(set(match_ids))

###############################################################################


def extract_vod_urls(url):
    """
    Extract YouTube URLs from Liquipedia URL
    """
    youtube_urls = {}

    html = requests.get(url).content.decode()
    soup = BeautifulSoup(html, 'lxml')
    url_divs = soup.select('div.bracket-popup-footer.plainlinks.vodlink')
    for div in url_divs:
        div_links = div.find_all('a')
        vod_links = [(link['title'], link) for link in div_links
                     if ('title' in link.attrs and
                         'watch game' in link['title'].lower())]
        dotabuff_links = [(link['title'], link) for link in div_links
                          if ('href' in link.attrs and
                              'title' in link.attrs and
                              'dotabuff.com' in link['href'])]
        for vl in vod_links:
            for dl in dotabuff_links:
                pattern = r'.*(Game \d+).*'
                m1 = re.match(pattern, vl[0])
                m2 = re.match(pattern, dl[0])
                if m1 and m2 and m1.group(1) == m2.group(1):
                    match_id = dl[1]['href'].split('/')[-1]
                    youtube_urls[match_id] = vl[1]['href']

    return youtube_urls

###############################################################################
