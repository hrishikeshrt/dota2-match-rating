#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 01:10:15 2019

@author: Hrishikesh Terdalkar
"""

import os
import time
import json
import logging
from urllib.parse import urlsplit, urlunsplit

import requests

import settings

###############################################################################

logger = logging.getLogger(__name__)
opendota_api = 'https://api.opendota.com/api'
data_dir = settings.data_dir

if not os.path.isdir(data_dir):
    os.makedirs(data_dir)

###############################################################################


def fetch_data(url, post=False, filename=None, query_data={}, update=False):
    '''
    Generic function to fetch data from opendota API

    @params:
        url: api url to query
        filename: save the data to this file
        query_data: query_data (default: {})
        update: if True, data is updated and overwritten (default: False)

    '''
    global opendota_api

    path = None
    if filename is not None:
        path = os.path.join(data_dir, filename)
        if not update and os.path.isfile(path):
            try:
                with open(path, 'r') as f:
                    json_data = json.load(f)
                logger.info(
                    f"Loading previously downloaded data from '{filename}'."
                )
                return json_data
            except Exception:
                pass

    time.sleep(5)
    url_parts = list(urlsplit(opendota_api))
    url_parts[2] += url
    url_parts[3] = '&'.join([f'{k}={v}' for k, v in query_data.items()])

    query_url = urlunsplit(url_parts)
    logger.info("Query URL:", query_url)

    r = requests.get(query_url) if not post else requests.post(query_url)
    content = r.content.decode('utf-8')
    json_data = json.loads(content)

    if json_data and 'error' in json_data:
        logger.warning(f"Could not fetch '{url}' ({json_data['error']}).")
        return None

    if path is not None:
        with open(path, 'w') as f:
            json.dump(json_data, f, ensure_ascii=False)
    return json_data

###############################################################################


def get_schema(update=False):
    url = '/schema'
    filename = 'schema.json'
    return fetch_data(url, filename=filename, update=update)

###############################################################################


def request_parse(match_id):
    url = f'/request/{match_id}'
    return fetch_data(url, post=True)


def request_status(job_id):
    url = f'/request/{job_id}'
    return fetch_data(url)

###############################################################################


def get_constants(resource=None, update=False):
    constants = {}

    if resource is not None:
        url = f'/constants/{resource}'
        filename = f'constants_{resource}.json'
        constants[resource] = fetch_data(url, filename=filename, update=update)
    else:
        url = '/constants'
        filename = 'constants.json'
        resources = fetch_data(url, filename=filename, update=update)
        for resource in resources:
            url = f'/constants/{resource}'
            filename = f'constants_{resource}.json'
            constants[resource] = fetch_data(url, filename=filename,
                                             update=update)
    return constants

###############################################################################


def get_heroes(update=False):
    url = '/heroes'
    filename = 'heroes.json'
    return fetch_data(url, filename=filename, update=update)


def get_hero_stats(update=False):
    url = '/heroStats'
    filename = 'hero_stats.json'
    return fetch_data(url, filename=filename, update=update)


def get_hero_benchmarks(hero_id, update=False):
    url = '/benchmarks'
    filename = f'benchmarks_{hero_id}.json'
    query_data = {
        'hero_id': hero_id
    }
    return fetch_data(url, filename=filename,
                      query_data=query_data, update=update)


###############################################################################


def get_teams(update=False):
    url = '/teams'
    filename = 'teams.json'
    teams = fetch_data(url, filename=filename, update=update)
    for team in teams:
        filename = f"team_{team['team_id']}.json"
        path = os.path.join(data_dir, filename)

        with open(path, 'w') as f:
            json.dump(team, f, ensure_ascii=False)
    return teams


def get_team(team_id, update=False):
    url = f'/teams/{team_id}'
    filename = f'team_{team_id}.json'
    return fetch_data(url, filename=filename, update=update)

###############################################################################


def get_match(match_id, update=False):
    url = f'/matches/{match_id}'
    filename = f'match_{match_id}.json'
    query_data = {}
    return fetch_data(url, filename=filename,
                      query_data=query_data, update=update)


def get_leagues(update=False):
    url = '/leagues'
    filename = 'leagues.json'
    return fetch_data(url, filename=filename, update=update)

###############################################################################


def get_player_matches(player_id, request=False, days=180, update=False):
    url = f'/players/{player_id}/matches'
    filename = f'player_{player_id}_matches.json'
    query_data = {
        'date': days
    }
    matches = fetch_data(url, filename=filename,
                         query_data=query_data, update=update)
    if request:
        for match in matches:
            match_id = match['match_id']
            if match['version'] is None or match['version'] < 20:
                json_data = request_parse(match_id)
                logger.info("Match ID:", match_id)
                logger.info("Job ID:", json_data['job']['jobId'])
    return matches


def get_pro_matches(update=False):
    url = '/proMatches'
    filename = 'pro_matches.json'
    return fetch_data(url, filename=filename, update=update)

###############################################################################


def update_data(frequent=True, infrequent=False, moderate=False):
    # frequent
    if frequent:
        get_teams(update=True)

    # infrequent
    if infrequent:
        get_constants(update=True)
        heroes = get_heroes(update=True)

    # moderate
    if moderate:
        heroes = get_heroes()
        for hero in heroes:
            get_hero_benchmarks(hero['id'], update=True)

###############################################################################
