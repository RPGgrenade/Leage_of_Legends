import time
from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import JSONValueProtocol
import RiotWeightConstants as Weights
import json
import math
import numpy as np
import matplotlib.pyplot as plt


class PopularChampionsInRanked(MRJob):

    def get_key_in_stats(self,stats, key_word, weight, is_bool = False):
        if key_word in stats:
            if not is_bool:
                return stats[key_word] * weight
            else:
                if stats[key_word]:
                    return weight
                else:
                    return 0
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

                rank = math.pow(rank_importance, Weights.RANK[player['highestAchievedSeasonTier']])
                win = Weights.WIN[stats['win']]

                important_weight = Weights.STATS["Important"]
                very_important_weight = Weights.STATS["Very Important"]

                total_damage = (self.get_key_in_stats(stats,'totalDamageDealt', important_weight))/champion_health_average #these numbers are very high, might influence scores too much
                gold_spent = (self.get_key_in_stats(stats,'goldSpent', very_important_weight))/item_price_average
                magic_damage = self.get_key_in_stats(stats,'magicDamageDealt', important_weight)/champion_health_average #can also be a huge number

                total_time_crowd_control = self. get_key_in_stats(stats,'totalTimeCrowdControlDealt',important_weight)
                longest_living_time = self.get_key_in_stats(stats, 'longestTimeSpentLiving', important_weight)
                deaths = self.get_key_in_stats(stats,'deaths', important_weight)
                wards_placed = self.get_key_in_stats(stats,'wardsPlaced', very_important_weight)
                turret_kills = self.get_key_in_stats(stats,'turretKills', very_important_weight)
                kills = self.get_key_in_stats(stats,'kills', important_weight)
                double_kills = self.get_key_in_stats(stats,'doubleKills', important_weight)
                neutral_minion_kills = self.get_key_in_stats(stats, 'neutralMinionsKilled', very_important_weight)
                champ_level = self.get_key_in_stats(stats, 'champLevel', very_important_weight)
                wards_killed = self.get_key_in_stats(stats, 'wardsKilled', very_important_weight)
                total_minions_killed = self.get_key_in_stats(stats, 'totalMinionsKilled', very_important_weight)
                wards_bought = self.get_key_in_stats(stats, 'sightWardsBoughtInGame', very_important_weight)
                inhibitor_kills = self.get_key_in_stats(stats, 'inhibitorKills', important_weight)
                time_ccing = self.get_key_in_stats(stats, 'timeCCingOthers', important_weight)

                first_inhibitor_skill = self.get_key_in_stats(stats,'firstInhibitorKill', very_important_weight, True)
                first_blood_assist = self.get_key_in_stats(stats,'firstBloodAssist', very_important_weight, True)
                first_blood_kill = self.get_key_in_stats(stats,'firstBloodKill', very_important_weight, True)
                first_tower_kill = self.get_key_in_stats(stats,'firstTowerKill', very_important_weight, True)
                first_tower_assist = self.get_key_in_stats(stats,'firstTowerAssist', very_important_weight, True)

                utility = total_damage + total_time_crowd_control + longest_living_time - deaths #+ gold_earned
                + wards_placed + turret_kills + gold_spent + magic_damage + kills + double_kills + neutral_minion_kills
                + champ_level + wards_killed + total_minions_killed + wards_bought + inhibitor_kills + time_ccing + first_inhibitor_skill
                + first_blood_assist + first_blood_kill + first_tower_kill + first_tower_assist

                score = utility * win * rank

                champ_id = player['championId']

                yield champ_id, [utility, score]

    def reducer_score_plot(self, champ_id, values):

        util_scores = [u_s for u_s in values]
        utilities = [u[0] for u in util_scores]
        scores = [s[1] for s in util_scores]

        champion_name = champ_data['data'][str(champ_id)]['name']

        champion_names.append(champion_name)
        champion_scores.append(sum(scores))
        champion_utilities.append(sum(utilities))
        champion_full_scores[champion_name] = scores

        yield champ_id, [sum(utilities),sum(scores)]

    def steps(self):
        return [MRStep(mapper=self.mapper_match_champion_scores),
                MRStep(reducer=self.reducer_score_plot)]


def normal_distribution(champion_count):
    score_array = np.array(champion_scores)
    highest_indexes = np.argpartition(score_array, -champion_count)[-champion_count:]
    lowest_indexes = np.argpartition(score_array, champion_count)[:champion_count]
    #indexes = np.concatenate([highest_indexes,lowest_indexes])

    plot_distribution(highest_indexes, True)
    plot_distribution(lowest_indexes, False)


def plot_distribution(indexes, is_top):
    for index in indexes:
        name = champion_names[index]
        scores = champion_full_scores[name]
        variance = np.var(scores)
        mean = np.mean(scores)

        x = mean + (variance ** 0.5) * np.random.randn(10000)
        plt.hist(x, 50)

        plt.xlabel('usefulness')
        plt.ylabel('probability')
        title = ''
        if is_top:
            title = name + ' (10 Best)'
        else:
            title = name + ' (10 Worst)'
        plt.title(title)
        plt.axis([-300000000, 300000000, 0, 1000])
        plt.show()


def plot_character_totals(totals, title):
    plt.title(title)
    plt.bar(champion_names, totals)
    plt.show()

champion_names = []
champion_scores = []
champion_utilities = []

champion_full_scores = dict()

rank_importance = 7 #the higher the number the more important higher ranks are considered
champ_data = json.load(open('champions_data.json'))
champion_health_average = 2000
item_price_average = 3000


if __name__ == '__main__':
    start = time.time()
    PopularChampionsInRanked.run()

    plot_character_totals(champion_scores, 'Success in Matches')
    plot_character_totals(champion_utilities, 'Individual Utility')
    normal_distribution(10)

    end = time.time()
    print("Time: " + str(end - start) + " sec")