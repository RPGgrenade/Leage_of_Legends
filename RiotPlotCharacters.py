import time
from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import JSONValueProtocol
import sys
import re
import itertools
import csv
import string
import RiotWeightConstants as Weights
import json
import math
import numpy as np
import matplotlib.pyplot as plt

champion_ids = []
champion_scores = []

class PopularChampionsInRanked(MRJob):

    def get_key_in_stats(self,stats, key_word, weight):
        if key_word in stats:
            return stats[key_word] * weight
        else:
            return 0

    def mapper_match_champion_scores(self, _, line):
        match = json.loads(line)
        if 'status' not in match: #error code accidentally stored if is the case

            teams = match['teams']
            team_id_win = dict()
            for team in teams:
                team_id_win[team['teamId']] = team['win']

            players = match['participants']
            for player in players: #there are no champion repeats in ranked games
                stats = player['stats']
                rank = math.pow(2, Weights.RANK[player['highestAchievedSeasonTier']])
                win = Weights.WIN[stats['win']]

                important_weight = Weights.STATS["Important"]
                very_important_weight = Weights.STATS["Very Important"]

                total_damage = self.get_key_in_stats(stats,'totalDamageDealt', important_weight)
                total_time_crowd_control = self. get_key_in_stats(stats,'totalTimeCrowdControlDealt',important_weight)
                longest_living_time = self.get_key_in_stats(stats, 'longestTimeSpentLiving', important_weight)
                gold_earned = self.get_key_in_stats(stats,'goldEarned', very_important_weight) #these numbers are very high, might influence scores too much
                deaths = self.get_key_in_stats(stats,'deaths', important_weight)
                wards_placed = self.get_key_in_stats(stats,'wardsPlaced', very_important_weight)
                turret_kills = self.get_key_in_stats(stats,'turretKills', very_important_weight)
                gold_spent = self.get_key_in_stats(stats,'goldSpent', very_important_weight)
                magic_damage = self.get_key_in_stats(stats,'magicDamageDealt', important_weight) #can also be a huge number
                kills = self.get_key_in_stats(stats,'kills', important_weight)
                double_kills = self.get_key_in_stats(stats,'doubleKills', important_weight)
                neutral_minion_kills = self.get_key_in_stats(stats, 'neutralMinionsKilled', very_important_weight)
                champ_level = self.get_key_in_stats(stats, 'champLevel', very_important_weight)
                wards_killed = self.get_key_in_stats(stats, 'wardsKilled', very_important_weight)
                total_minions_killed = self.get_key_in_stats(stats, 'totalMinionsKilled', very_important_weight)
                wards_bought = self.get_key_in_stats(stats, 'sightWardsBoughtInGame', very_important_weight)
                inhibitor_kills = self.get_key_in_stats(stats, 'inhibitorKills', important_weight)
                time_ccing = self.get_key_in_stats(stats, 'timeCCingOthers', important_weight)

                first_inhibitor_skill = 0
                first_blood_assist = 0
                first_blood_kill = 0
                first_tower_kill = 0
                first_tower_assist = 0
                if 'firstInhibitorKill' in stats:
                    if stats['firstInhibitorKill']:
                        first_inhibitor_skill = very_important_weight
                if 'firstBloodAssist' in stats:
                    if stats['firstBloodAssist']:
                        first_blood_assist = very_important_weight
                if 'firstBloodKill' in stats:
                    if stats['firstBloodKill']:
                        first_blood_kill = very_important_weight
                if 'firstTowerKill' in stats:
                    if stats['firstTowerKill']:
                        first_tower_kill = very_important_weight
                if 'firstTowerAssist' in stats:
                    if stats['firstTowerAssist']:
                        first_tower_assist = very_important_weight

                utility = total_damage + total_time_crowd_control + longest_living_time + gold_earned - deaths \
                + wards_placed + turret_kills + gold_spent + magic_damage + kills + double_kills + neutral_minion_kills \
                + champ_level + wards_killed + total_minions_killed + wards_bought + inhibitor_kills + time_ccing + first_inhibitor_skill \
                + first_blood_assist + first_blood_kill + first_tower_kill + first_tower_assist

                score = utility * win * rank

                champ_id = player['championId']

                yield champ_id, [utility, score]

    def reducer_score_plot(self, champ_id, values):
        util_scores = [u_s for u_s in values]
        utilities = [u[0] for u in util_scores]
        scores = [s[1] for s in util_scores]
        champion_ids.append(champ_id)
        champion_scores.append(sum(scores))
        yield champ_id, [sum(utilities),sum(scores)]

    def steps(self):
        return [MRStep(mapper=self.mapper_match_champion_scores),
                MRStep(reducer=self.reducer_score_plot)]


if __name__ == '__main__':
    start = time.time()
    PopularChampionsInRanked.run()
    end = time.time()
    print("Time: " + str(end - start) + " sec")
    plt.bar(champion_ids, champion_scores)
    plt.show()