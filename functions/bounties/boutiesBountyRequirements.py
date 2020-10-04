"""
Template:

"Description": {
    "requirements": ["a", "b"],     # what requirements does the role have
    "a": ...,                       # details on the requirement
    "b": ...,

    "points": integer               # how many points the completion / win gives
}


Current requirements:

randomActivity      # one value will automatically get changed to allowedActivities during selection process. Needs to be in double brackets since there might be multiple hashes per activity - input: [[1, 2], [3, 4]]; output = [3, 4]
allowedActivities   # list - which directorActivityHash are allowed
allowedTypes        # which activity type hashes are allow, fe. activityTypeHash: 1686739444 is story
speedrun            # bounties: requires a number if allowedTypes is given, and an entry in speedrunActivities if allowedActivities is given
lowman
contest             # how far below the recommeneded light for the activity one has to be
firstClear          # list - out of which activities has the current one to be the first
noWeapons
customLoadout       # after processing formating will be {kineticHash: "Hand Cannon", ...}
kd
totalKills
totalDeaths
NFscore
flawless            # sets score to one if thats in it. To track lighthouse visits
win                 # activity did not just get completed, but standing is "Victory"
winStreak           # requires win to also be an recquirement
tournament          # starts registration for the pvp tournament

extra_text          # will show more text
points              # how many points the user gets for completing the bounty

"""

""" Hashes:"""
from static.dict import *

# ----------------------------------------------------------------------------------
"""
Points:
    Normal Bounties:
        50-100
        
    Competitive Bounties:
        200-300
"""
# ----------------------------------------------------------------------------------
# bounties:
bounties_dict = {
    # raid bounties
    'Raids': {
        # new players
        "New Players": {
            "Clear a raid for the first time": {
                "requirements": ["allowedTypes", "firstClear"],
                "allowedActivities": activityRaidHash,
                "firstClear": raidHashes,
                "extraText": "If you already cleared all raids at \nleast once, you can not complete \nthis bounty, sorry",
                "points": 80
            },

            "Finish a raid": {
                "requirements": ["allowedTypes"],
                "allowedTypes": activityRaidHash,
                "points": 60
            },

            "Finish a dungeon": {
                "requirements": ["allowedTypes"],
                "allowedTypes": activityDungeonHash,
                "points": 50
            }
        },

        # experienced players
        "Experienced Players": {
            "Do a lowman of any raid": {
                        "requirements": ["allowedTypes", "lowman"],
                        "allowedTypes": activityRaidHash,
                        "lowman": [3, 2, 1],
                        "extraText": "Solo, duo or trio are allowed",
                        "points": [80, 100, 120]
                    },

            "Do a raid with a specific loadout": {
                "requirements": ["allowedTypes", "customLoadout"],
                "allowedTypes": activityRaidHash,
                "extraText": "Kinetic: ? \nEnergy: % \nPower: & ",
                "points": 60
            },

            "Do a dungeon with a specific loadout": {
                "requirements": ["allowedTypes", "customLoadout"],
                "allowedTypes": activityDungeonHash,
                "extraText": "Kinetic: ? \nEnergy: % \nPower: & ",
                "points": 50
            },

            "Finish a raid within the allowed time frame": {
                "requirements": ["allowedTypes", "speedrun"],
                "allowedTypes": activityRaidHash,
                "extraText": "",
                "points": 80
            },

            "Finish a raid with the contest modifier": {
                "requirements": ["allowedTypes", "contest"],
                "allowedTypes": activityRaidHash,
                "contest": 20,
                "extraText": "You have to be at least 20 power\n below recommended. \nOnly you have to be lower light",
                "points": 80
            },

            "Do a flawless raid": {
                "requirements": ["allowedTypes", "totalDeaths"],
                "allowedTypes": activityRaidHash,
                "totalDeaths": 0,
                "extraText": "Only you don't have to die",
                "points": 60
            },

            "Do a flawless dungeon": {
                "requirements": ["allowedTypes", "totalDeaths"],
                "allowedTypes": activityDungeonHash,
                "totalDeaths": 0,
                "extraText": "Only you don't have to die",
                "points": 50
            }
        }
    },


    # general pve bounties
    'PvE': {
        # new players
        "New Players": {
            "Finish a strike": {
                "requirements": ["allowedTypes", "totalKills", "totalDeaths"],
                "allowedTypes": activityStrikeAndNFHash,
                "totalDeaths": 1,
                "totalKills": 100,
                "extraText": "While getting high kills (100) \nand low deaths (1)",
                "points": 60
            },

            "Clear an adventure with a specific loadout": {
                "requirements": ["allowedTypes", "customLoadout"],
                "allowedTypes": activityStoryHash,
                "extraText": "Kinetic: ? \nEnergy: % \nPower: & ",
                "points": 50
            },

            "Complete a Nightfall": {
                "requirements": ["allowedTypes"],
                "allowedTypes": activityNFHash,
                "points": 40
            }
        },

        # experienced players
        "Experienced Players": {
            "Finish a strike": {
                "requirements": ["allowedTypes", "speedrun", "totalKills", "totalDeaths"],
                "allowedTypes": activityStrikeAndNFHash,
                "speedrun": 600,
                "totalDeaths": 0,
                "totalKills": 100,
                "extraText": "While getting high kills (100), \nlow deaths (0) and finishing in \nunder 10 minutes",
                "points": 70
            },

            # not implemented yet bc BL will probly change everything here
            #
            # "Clear this daily heroic adventure within the allowed time frame": {
            # },

            "Complete a Nightfall": {
                "requirements": ["allowedTypes", "NFscore"],
                "allowedTypes": activityNFHash,
                "NFscore": 150_000,
                "extraText": "You have to get a high score (150k)",
                "points": 60
            }
        }
    },


    # pvp bounties
    'PvP': {
        # new players
        "New Players": {
            "Win a crucible game": {
                "requirements": ["allowedTypes", "win", "kd"],
                "allowedTypes": activityPVPHash,
                "kd": 1,
                "extraText": "While also having a positive K/D",
                "points": 50
            },

            "Get a win streak in the crucible": {
                "requirements": ["allowedTypes", "winStreak"],
                "allowedTypes": activityPVPHash,
                "winStreak": 3,
                "extraText": "You need a win streak of 3",
                "points": 80
            }
        },

        # experienced players
        "Experienced Players": {
            "Get a win streak in the crucible": {
                "requirements": ["allowedTypes", "winStreak"],
                "allowedTypes": activityPVPHash,
                "winStreak": 5,
                "extraText": "You need a win streak of 5",
                "points": 80
            },

            "Win a crucible game": {
                "requirements": ["allowedTypes", "win", "kd"],
                "allowedTypes": activityPVPHash,
                "kd": 3,
                "extraText": "While also having a K/D > 3",
                "points": 50
            },

            "Win a crucible game ": {
                "requirements": ["allowedTypes", "win", "totalKills"],
                "allowedTypes": activityPVPHash,
                "totalKills": 30,
                "extraText": "While also getting \na high amount of kills (30)",
                "points": 50
            },

            "Win a crucible game  ": {
                "requirements": ["allowedTypes", "win", "totalDeaths"],
                "allowedTypes": activityPVPHash,
                "totalDeaths": 0,
                "extraText": "You are not allowed to die",
                "points": 80
            }
        }
    }
}

# ----------------------------------------------------------------------
# bounties where the whole clan competes against each other
competition_bounties_dict = {
    # raid bounties
    'Raids': {
        "Get the fastest clear of the raid ?": {
            "requirements": ["randomActivity", "speedrun"],
            "randomActivity": raidHashes,
            "extraText": "Everyone in your fireteam gets \ncredit for the bounty",
            "points": 250
        },

        "Get the fastest clear of the dungeon ?": {
            "requirements": ["randomActivity", "speedrun"],
            "randomActivity": dungeonHashes,
            "extraText": "Everyone in your fireteam gets \ncredit for the bounty",
            "points": 200
        },

        "Do a lowman (solo, duo or trio) of ?": {
            "requirements": ["randomActivity", "lowman"],
            "randomActivity": raidHashes,
            "extraText": "Everyone in your fireteam gets \ncredit for the bounty",
            "points": 300
        },

        "Get the fastest clear of the raid ? ": {
            "requirements": ["randomActivity", "speedrun", "noWeapons"],
            "randomActivity": raidHashes,
            "extraText": "Only ability kills are allowed, \ndon't bring weapons",
            "points": 300
        },
    },


    # general pve bounties
    'PvE': {
        # not implemented yet bc BL will probly change everything here
        #
        # "Get the fastest completion of this daily heroic story mission": {
        # },

        "Get the most kills in a gambit match": {
            "requirements": ["allowedTypes", "totalKills"],
            "allowedTypes": activityGambitHash,
            "points": 200
        },

        "Get the highest Nightfall Score": {
            "requirements": ["allowedTypes", "NFscore"],
            "allowedTypes": activityNFHash,
            "extraText": "Everyone in your fireteam gets \ncredit for the bounty",
            "points": 250
        }
    },


    # pvp bounties
    'PvP': {
        "Get the highest kills in a game in any PvP mode": {
            "requirements": ["allowedTypes", "totalKills"],
            "allowedTypes": activityPVPHash,
            "points": 200
        },

        "Get the best K/D in a game in any PvP mode": {
            "requirements": ["allowedTypes", "kd"],
            "allowedTypes": activityPVPHash,
            "points": 200
        },

        "Go Flawless and visit the Lighthouse": {
            "requirements": ["allowedTypes"],
            "allowedTypes": activityLighthouseHash,
            "points": 250
        },

        "Win this weeks PvP tournament": {
            "requirements": ["tournament", "flawless"],
            "extraText": "For registration, visit \n#tournament",
            "points": 300
        }
    }
}
