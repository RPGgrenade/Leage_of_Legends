import time
from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import JSONValueProtocol
import RiotWeightConstants as Weights
import json
import math
import numpy as np
import matplotlib.pyplot as plt
import csv
import csv_data


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

    def get_character_strategy_weight(self, champ_id, lane_role):
        champion_name = champ_data['data'][str(champ_id)]['name']
        try:
            strat_numbers = champion_strat_count[champion_name]
            lane = lane_role[0]
            role = lane_role[1]
            lane_number = int(strat_numbers[lane])
            role_number = int(strat_numbers[role])
            lane_weight = Weights.LANES[lane]
            role_weight = Weights.ROLES[role]
            return (lane_number*lane_weight + role_number*role_weight)
        except:
            return 0


    def mapper_match_champion_scores(self, _, line):
        match = json.loads(line)
        if 'status' not in match: #error code accidentally stored if is the case

            teams = match['teams']
            #team_id_win = dict()
            #for team in teams:
            #    team_id_win[team['teamId']] = team['win']

            players = match['participants']
            for player in players: #there are no champion repeats in ranked games

                stats = player['stats']

                if 'highestAchievedSeasonTier' in player:
                    rank = math.pow(rank_importance, Weights.RANK[player['highestAchievedSeasonTier']])
                else:
                    rank = 0
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

                lane = player['timeline']['lane']
                role = player['timeline']['role']

                team_position = [lane, role]
                champ_id = player['championId']
                strategy_weight = self.get_character_strategy_weight(champ_id, team_position)

                utility = (total_damage + total_time_crowd_control + longest_living_time - deaths #+ gold_earned
                + wards_placed + turret_kills + gold_spent + magic_damage + kills + double_kills + neutral_minion_kills
                + champ_level + wards_killed + total_minions_killed + wards_bought + inhibitor_kills + time_ccing + first_inhibitor_skill
                + first_blood_assist + first_blood_kill + first_tower_kill + first_tower_assist + strategy_weight)

                score = utility * win * rank

                yield champ_id, [utility, score, team_position]

    def reducer_score_plot(self, champ_id, values):

        util_score_positions = [u_s for u_s in values]

        utilities = [u[0] for u in util_score_positions]
        scores = [s[1] for s in util_score_positions]
        positions = [s[2] for s in util_score_positions]

        champion_name = champ_data['data'][str(champ_id)]['name']

        champion_names.append(champion_name)
        champion_scores.append(sum(scores))
        champion_utilities.append(sum(utilities))
        champion_full_scores[champion_name] = scores
        champion_positions[champion_name] = positions


    def steps(self):
        return [MRStep(mapper=self.mapper_match_champion_scores),
                MRStep(reducer=self.reducer_score_plot)]


def normal_distribution(champion_count):
    score_array = np.array(champion_scores)
    highest_indexes = np.argpartition(score_array, -champion_count)[-champion_count:]
    lowest_indexes = np.argpartition(score_array, champion_count)[:champion_count]

    plot_distribution(highest_indexes,champion_count, True)
    plot_distribution(lowest_indexes, champion_count, False)
    plot_lanes_roles(highest_indexes)
    plot_lanes_roles(lowest_indexes)


def plot_lanes_roles(indexes):
    for index in indexes:
        name = champion_names[index]
        lane_roles = champion_positions[name]
        lanes_count = dict()
        roles_count = dict()
        for lr in lane_roles:
            lane = lr[0]
            role = lr[1]
            if lane not in lanes_count:
                lanes_count[lane] = 1
            else:
                lanes_count[lane] += 1

            if role not in roles_count:
                roles_count[role] = 1
            else:
                roles_count[role] += 1

        champion_strat_count[name] = {**roles_count, **lanes_count}
        #plot_champion_position_count(roles_count, lanes_count, name)

def plot_champion_position_count(roles_data, lanes_data, name):
    roles = list(roles_data.keys())
    role_counts = list(roles_data.values())
    lanes = list(lanes_data.keys())
    lane_counts = list(lanes_data.values())

    role_plot = plt.subplot(2,1,1)
    plt.title(name + ' Roles & Lanes')
    plt.bar(roles, role_counts)
    lane_plot = plt.subplot(2,1,2)
    plt.bar(lanes, lane_counts)
    plt.show()


def plot_distribution(indexes, count, is_top):
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
            title = name + ' ('+ str(count) +' Best)'
        else:
            title = name + ' ('+ str(count) +' Worst)'
        plt.title(title)
        plt.axis([-300000000, 300000000, 0, 1000])
        plt.show()


def plot_character_totals(totals, title):
    plt.title(title)
    plt.bar(champion_names, totals)
    plt.show()


def generate_from_csv(file):
        reader = csv.reader(file)
        for line in reader:
            if len(line) > 0:
                name = line[0]
                support = line[1]
                duo_support = line[2]
                none = line[3]
                solo = line[4]
                duo = line[5]
                duo_carry = line[6]
                top = line[7]
                middle = line[8]
                jungle = line[9]
                bottom = line[10]
                champion_strat_count[name] = dict()
                champion_strat_count[name]['SUPPORT'] = support
                champion_strat_count[name]['DUO_SUPPORT'] = duo_support
                champion_strat_count[name]['NONE'] = none
                champion_strat_count[name]['SOLO'] = solo
                champion_strat_count[name]['DUO'] = duo
                champion_strat_count[name]['DUO_CARRY'] = duo_carry
                champion_strat_count[name]['TOP'] = top
                champion_strat_count[name]['MIDDLE'] = middle
                champion_strat_count[name]['JUNGLE'] = jungle
                champion_strat_count[name]['BOTTOM'] = bottom

champion_names = []
champion_scores = []
champion_utilities = []

champion_full_scores = dict()
champion_positions = dict()

champion_strat_count = dict()

rank_importance = 7 #the higher the number the more important higher ranks are considered
champ_data = json.load(open('champions_data.json'))
champion_health_average = 2000
item_price_average = 3000


if __name__ == '__main__':
    start = time.time()
    generate_from_csv(open("champ_strategies_preseason.csv", 'r'))
    PopularChampionsInRanked.run()
    end = time.time()
    print("Time: " + str(end - start) + " sec")

    plot_character_totals(champion_scores, 'Success in Matches')
    plot_character_totals(champion_utilities, 'Individual Utility')
    normal_distribution(10)
    #csv_data.make_csv("champ_strategies_preseason", champion_strat_count)
