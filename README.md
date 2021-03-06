# DotA2 Match-Rating System

Figure out which games you should not miss.

**Note**

Several metrics are dependent on team ratings, recent hero pick/ban rate, hero benchmarks etc. So, the scoring will not give ideal results for older matches.

## Requirements

- python3.6+
- PyPI requirements in `requirements.txt`
- `pip3 install -r requirements.txt`

## Scoring Metrics

Several metrics are used to assign a score either,
* Normalized to be between 0 to 1
* Normalized using standard numbers (so that it's *roughly* between 0 to 1)

Some of the notable metrics are described below. One's perception of importance of various metrics can be different, and therefore the weightage for those can be edited in
`settings.py`

### Length-related

* Longer matches might be more interesting.
* Matches wih many teamfights, many kills, rapier purchases, rapier drops, aegis snatches etc. might be more interesting.

**Note**: While these might be influenced by the match length, they are not the exact same thing.


### Advantage Flips

* Calculate flips in the advantage in Gold and Experience.
* More flips usually make for an interesting match.

### Off-meta or Benchmark-related

* Meta can be defined by roughly examining recent pro matches and top N picks, bans.
* Off-meta picks might be more interesting.
* Matches where benchamrks on specific hero are superceded might be more interesting

### Team Ratings

* Teams with similar rating may be more interesting.
* Teams with higher rating may be more interesting.

### Surprise Factor
Assign higher score for either a close match between mismatched teams, or a stomp between closely matched teams.

**Note**: Surprise factor implementation is still not ideal, since it uses team ratings to determine whether teams are equally matched or not, and the team rating is often not an exact measure of skill.

## Usage

* Modify and copy `settings.sample.py` to `settings.py`.
* Score a single match and show details: `python3 score.py -m <match_id>`
* Score all matches from a league: `python3 score.py -u <liquipedia_url_of_league>`
* Score multiple matches: `python3 score.py -M <match_id_1> <match_id_2> ..`
