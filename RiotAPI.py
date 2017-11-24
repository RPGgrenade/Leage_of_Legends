import RiotConstants as Consts
import requests
import json
import random
import time
import datetime
from pymongo import MongoClient

class RiotAPI(object):

    def __init__(self, api_key, region=Consts.REGIONS['KR']):
        self.api_key = api_key
        self.region = region
        self.accountId = 0
        self.matchId = 0
        self.json_name = None

    def _request(self, api_url, params=[]):
        args = {'api_key': self.api_key}
        for key, value in params:
            if key not in args:
                args[key] = value

        response = requests.get(
            Consts.URL['base'].format(
                region=self.region,
                request=api_url
            ),
            params=args)
        return response.json()

    def get_random_seed(self, json_name):
        self.json_name = json_name
        json_file = open(self.json_name)
        json_data = json.load(json_file)

        matches_list = list(json_data['matches'])
        while True:
            match = random.choice(matches_list) #get a random match from the list
            is_preseason_2018 = self.is_after_date(match,2017,11,7)
            if is_preseason_2018:
                break

        self.update_random_user(match)

    def is_after_date(self, match, Y, M, D):
        try:
            timestamp = match['gameCreation']
        except:
            timestamp = match['timestamp']
        date = datetime.datetime.utcfromtimestamp(timestamp / 1000)
        year = date.year
        month = date.month
        day = date.day
        is_season = year >= Y and month >= M and day >= D
        return is_season

    def update_random_user(self, match):
        users_list = list()
        try:
            users_list = list(match['participantIdentities'])
            user = random.choice(users_list)['player']
            self.accountId = user['accountId']
            self.region = user['currentPlatformId']
        except:
            self.get_random_seed(self.json_name)


    def get_random_ranked_match(self):
        matches = self.get_by_id(self.accountId,type='User Matches')
        matches_list = list(matches['matches'])
        ranked_matches = self.filter_ranked(matches_list)
        i = 0
        while True:
            match = random.choice(ranked_matches)
            i += 1
            if self.is_after_date(match, 2017, 11, 7):
                break
            if i > 1000:
                print("retrying")
                return None
        return match

    def filter_ranked(self, matches):
        ranked = []
        for match in matches:
            queue = match['queue']
            if queue in Consts.QUEUES.values():
                ranked.append(match)
        return ranked

    def get_by_id(self, id, type='Match'):
        api_url = Consts.REQUEST_TYPES[type].format(
            id=id
        )
        return self._request(api_url)


    #Plan for getting data:
    #1. Get a random player from a random match from a random seed data file
    #2. Get the accountId & region from said user and find the ranked matches they've played (User matches in the constants)
    #3. Get a random match, store its data after checking for specific data types (possibly finding out tiers)
    #4. Repeat
    #5. If there are no matches to find, start from the beginning and search for another random player from the seed data file
    #6. If you get a 403 response code run previous step (not yet implemented)


    #New strategy:
    #1. Find summoner names for recent players, possibly top players. In order to get more valuable information
    #2. If none are available (possible) or reach a dead end, restart using the seeding data, but only go for data with recent
    # timestamps (using an epoch converter to know how long ago it was (no more than before Nov 7th))
    #3. Get the newer matches this way, and keep them in their own collection of data.
    #4. Prune it the same way afterwards.

current_key = 'RGAPI-27c006be-1dfd-4536-9d14-ca5c33f02030' #Changes every day

def main():
    client = MongoClient('localhost', 27017)
    #db = client.test_database
    #collection = db.test_collection
    db = client.lol_database
    collection = db.preseason_2018
    api = RiotAPI(current_key)

    number = random.randint(1,5)
    #number = 4
    #json_name = "matches" + str(number) + ".json"
    json_name = "pro_matches.json"

    print("Seed " + json_name)
    api.get_random_seed(json_name)
    while True:
        try:
            ranked_match = api.get_random_ranked_match()
            api.matchId = ranked_match['gameId']
            match_data = api.get_by_id(api.matchId)
        except:
            match_data = api.get_by_id(api.matchId)
        print(match_data)
        data = collection.insert(match_data)
        print(str(db.command("collstats","preseason_2018")["size"]/1000000000) + " GB")
        print(str(db.preseason_2018.count()) + " Matches")
        #save it
        time.sleep(1)
        api.update_random_user(match_data)

if __name__ == '__main__':
    main()