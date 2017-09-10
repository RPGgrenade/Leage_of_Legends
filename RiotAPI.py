import RiotConstants as Consts
import requests
import json
import random
import time
from pymongo import MongoClient

class RiotAPI(object):

    def __init__(self, api_key, region=Consts.REGIONS['KR']):
        self.api_key = api_key
        self.region = region
        self.accountId = 0
        self.matchId = 0

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
        json_file = open(json_name)
        json_data = json.load(json_file)

        matches_list = list(json_data['matches']) #just a temp key until I find the actual term
        match = random.choice(matches_list) #get a random match from the list

        self.update_random_user(match)

    def update_random_user(self, match):
        users_list = list(match['participantIdentities'])  # temp key
        user = random.choice(users_list)['player']

        self.accountId = user['accountId']
        self.region = user['currentPlatformId']

    def get_random_ranked_match(self):
        matches = self.get_by_id(self.accountId,type='User Matches')
        matches_list = list(matches['matches'])
        ranked_matches = self.filter_ranked(matches_list)
        return random.choice(ranked_matches)

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
    #4. Repeat until a certain amount of matches have been stored

current_key = 'Insert Key Here' #Changes every day

def main():
    client = MongoClient('localhost', 27017)
    db = client.test_database
    collection = db.test_collection
    api = RiotAPI(current_key)
    number = random.randint(1,5)
    #number = 4
    json_name = "matches" + str(number) + ".json"
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
        #save it
        time.sleep(1)
        api.update_random_user(match_data)

if __name__ == '__main__':
    main()