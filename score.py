#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Score DotA2 Matches
"""

__author__ = "Hrishikesh Terdalkar"

###############################################################################

import logging
from collections import defaultdict

from tqdm import tqdm
import opendota

import utils
import settings

###############################################################################

logger = logging.getLogger(__name__)
api = opendota.OpenDota()

###############################################################################


def calculate_meta_scores(hero_stats):
    scores = {}
    picks = []
    bans = []
    contests = []

    for hero in hero_stats:
        picks.append(hero['pro_pick'])
        bans.append(hero['pro_ban'])
        contests.append(hero['pro_pick'] + hero['pro_ban'])

    max_contests = max(contests)
    total_contests = sum(contests)

    for hero in hero_stats:
        contest = hero['pro_pick'] + hero['pro_ban']
        scores[hero['id']] = sum([
            contest / max_contests,
            contest / total_contests
        ])
    return scores

###############################################################################


def calculate_flips_score(values):
    flip_count = 0
    flip_score = 0
    # flip_index = []

    max_value = abs(max(values, key=abs))
    for idx, (x1, x2, x3) in enumerate(zip(values, values[1:], values[2:])):
        if (x2 - x1) * (x3 - x2) < 0:
            flip_count += 1
            flip_score += abs(x3 - x2) / max_value
            # flip_index.append(idx + 2)

    return flip_count, flip_score


def calculate_match_score(match_id, config, **kwargs):
    """Assign score to a DotA2 Match"""
    match = api.get_match(match_id)

    weight_prefix = 'weight_'
    normalizer_prefix = 'normalizer_'

    for k, v in kwargs.items():
        if k.startswith(weight_prefix):
            config['weights'][k.replace(weight_prefix, '')] = v
        if k.startswith(normalizer_prefix):
            config['normalizers'][k.replace(normalizer_prefix, '')] = v

    # ----------------------------------------------------------------------- #
    # Scores

    team_radiant = api.get_team(match['radiant_team_id'])
    team_dire = api.get_team(match['dire_team_id'])

    # flips score
    gold_values = match['radiant_gold_adv']
    xp_values = match['radiant_xp_adv']
    gold_flips, gold_flips_score = calculate_flips_score(gold_values)
    xp_flips, xp_flips_score = calculate_flips_score(xp_values)

    # rating score
    max_rating = api.get_teams()[0]['rating']

    rating_average = (team_radiant['rating'] + team_dire['rating']) / 2
    rating_difference = abs(team_radiant['rating'] - team_dire['rating'])
    rating_better = max(team_radiant['rating'], team_dire['rating'])

    rating_average_score = rating_average / max_rating
    rating_difference_score = 1 - rating_difference / rating_better

    # kills score
    kills_total = match['radiant_score'] + match['dire_score']
    kill_difference = abs(match['radiant_score'] - match['dire_score'])
    kills_better = max(match['radiant_score'], match['dire_score'])

    # scores
    kills_score = (kills_total) / config['normalizers']['kills']
    kill_difference_score = 1 - kill_difference / kills_better

    # aegis scores
    aegis_pick = 0
    aegis_deny = 0
    aegis_stolen = 0

    for objective in match['objectives']:
        if objective['type'] == 'CHAT_MESSAGE_AEGIS':
            aegis_pick += 1
        if objective['type'] == 'CHAT_MESSAGE_AEGIS_STOLEN':
            aegis_stolen += 1

    aegis_pick_score = aegis_pick / config['normalizers']['aegis_pick']
    aegis_deny_score = aegis_deny / config['normalizers']['aegis_deny']
    aegis_stolen_score = aegis_stolen / config['normalizers']['aegis_stolen']

    # other scores
    duration_score = match['duration'] / config['normalizers']['duration']
    teamfights_count = len(match['teamfights'])
    teamfights_score = teamfights_count / config['normalizers']['teamfights']

    # player/hero based scores
    meta_score_total = 0
    benchmark_scores = defaultdict(int)
    rapier_count = 0

    for player in match['players']:
        hero_id = player['hero_id']
        benchmarks = player['benchmarks']
        rapier_count += player.get('purchase_rapier', 0)
        for k, v in benchmarks.items():
            benchmark_scores[k] += v['pct']

        meta_score_total += (1 - config['meta'][hero_id])

    # normalize
    rapier_score = rapier_count / config['normalizers']['rapier']
    meta_score = meta_score_total / 10
    for k, v in benchmarks.items():
        benchmark_scores[k] /= 10

    # surprise factor
    # TODO: consider if it is required
    # may be already captured via rating difference + flip score?

    # ----------------------------------------------------------------------- #

    metrics = {
        'duration': duration_score,
        'kills_total': kills_score,
        'kills_difference': kill_difference_score,
        'advantage_flips_gold': gold_flips_score,
        'advantage_flips_experience': xp_flips_score,
        'team_rating_average': rating_average_score,
        'team_rating_difference': rating_difference_score,
        'non_meta_picks': meta_score,
        'aegis_pick': aegis_pick_score,
        'aegis_deny': aegis_deny_score,
        'aegis_stolen': aegis_stolen_score,
        'rapier_pick': rapier_score,
        'rapier_drop': 0,  # information unavailable
        'teamfights': teamfights_score,
        'gold_per_min': benchmark_scores['gold_per_min'],
        'xp_per_min': benchmark_scores['xp_per_min'],
        'last_hits_per_min': benchmark_scores['last_hits_per_min'],
        'surprise_factor': 0,
    }

    # ----------------------------------------------------------------------- #

    score = sum([metrics[m] * config['weights'][m]
                 for m in metrics if m in config['weights']])

    match_info = {}
    match_info['id'] = match['match_id']
    match_info['score'] = score
    match_info['title'] = ' '.join([
        team_radiant['name'], 'vs.', team_dire['name']
    ])
    match_info['metrics'] = metrics

    return match_info

###############################################################################


def score_matches_from_league(league_url, config):
    """
    Score All Matches from DotA2 League

    Parameters
    ----------

    league_url: str
        Any URL that has all the match IDs from the league
        e.g. Liquipedia URL for the league

    Returns
    -------
    match_scores_sorted: list
        Sorted list of matches by scores
    """
    match_ids = utils.extract_match_ids(league_url)
    logger.info(f"Extracted {len(match_ids)} match-ids.")

    match_scores = {}
    for match_id in tqdm(match_ids):
        try:
            match_scores[match_id] = calculate_match_score(match_id, config)
        except Exception as e:
            logger.warning(f"Skipped ({match_id}): {e}")

    match_scores_sorted = sorted(match_scores.values(),
                                 key=lambda x: x['score'], reverse=True)

    return match_scores_sorted

###############################################################################


if __name__ == '__main__':
    import json
    import tabulate
    import argparse

    league_urls = settings.league_urls

    # defaults
    league_url = league_urls['dpc_eu_1_upper']

    # parser
    parser = argparse.ArgumentParser(description="Score DotA2 Matches")
    parser.add_argument("-u", "--url", help="Leage URL", default=league_url)
    parser.add_argument("-m", "--match", help="Match ID")
    args = vars(parser.parse_args())

    # processing
    hero_stats = api.get_hero_stats()
    meta = calculate_meta_scores(hero_stats)

    # scoring parameters
    config = {}
    config['meta'] = meta
    config['normalizers'] = settings.normalizers
    config['weights'] = settings.weights

    if args.get('match', None):
        score = calculate_match_score(args['match'], config)
        print(json.dumps(score, ensure_ascii=False, indent=2))
    else:
        match_scores = score_matches_from_league(args['url'], config)
        vod_urls = utils.extract_vod_urls(args['url'])

        opendota = 'https://www.opendota.com/matches/'
        headers = ['Match', 'Score', 'Details', 'VOD']
        print(tabulate.tabulate([[
                match['title'],
                match['score'],
                f"{opendota}{match['id']}",
                vod_urls.get(str(match['id']), "No VOD found.")
            ]
            for match in match_scores
        ], headers=headers, tablefmt='fancy_grid'))
