URL = {
    'base':'https://{region}.api.riotgames.com/lol/{request}'
}

QUEUES = {
    'Solo-Ranked': 4,
    'Duo-Ranked': 6,
    'Flex-Ranked': 9,
    'Team-Ranked-5v5': 42,
    'Team-Ranked-3v3': 41,
    'Ranked-Draft-5v5': 410,
    'Ranked-Solo-TeamBuilder': 420,
    'Ranked-Flex-5v5': 440
}

REQUEST_TYPES = {
    'Champions':'platform/v3/champions',
    'Champion':'platform/v3/champions/{id}',
    'Items':'static-data/v3/items',
    'Item':'static-data/v3/items/{id}',
    'Spells':'static-data/v3/summoner-spells',
    'Spell':'static-data/v3/summoner-spells/{id}',
    'Status':'status/v3/shard-data',
    'Masteries':'platform/v3/masteries/by-summoner/{id}',
    'Match':'match/v3/matches/{id}',
    'User Matches':'match/v3/matchlists/by-account/{id}',
    'Runes':'platform/v3/runes/by-summoner/{id}'
}

REGIONS = {
    'BR':'BR1', #Brazil
    'LAN': 'LA1', #Latin America North
    'LAS': 'LA2', #Latin America South
    'EUNE':'EUN1', #European North East
    'EUW':'EUW1', #European West
    'JP':'JP1', #Japan
    'KR':'KR', #Korea
    'NA':'NA', #North America
    'NA1':'NA1', #Newer North America
    'OCE':'OC1', #Oceania
    'TR':'TR1', #Turkey
    'RU':'RU', #Russia
    'PBE':'PBE1' #
}