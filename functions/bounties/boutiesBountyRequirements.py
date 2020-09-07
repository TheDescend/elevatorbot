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
completions
firstClear          # list - out of which activities has the current one to be the first
noWeapons
customLoadout       # after processing formating will be {kineticHash: "Hand Cannon", ...}
kd
totalKills
totalDeaths
NFscore
win                 # activity did not just get completed, but standing is "Victory"
winStreak           # requires win to also be an recquirement
tournament          #todo

extra_text          # will show more text
points              # how many points the user gets for completing the bounty

"""

""" Hashes:"""
from static.dict import *

# ----------------------------------------------------------------------------------
# bounties:
bounties = {
    # raid bounties
    'Raids': {
        # new players
        "New Players": {
            "Clear a raid for the first time": {
                "requirements": ["allowedActivities", "firstClear"],
                "allowedActivities": raidHashes,
                "firstClear": raidHashes,
                "points": 1
            },

            "Finish two raids": {
                "requirements": ["allowedTypes", "completions"],
                "allowedTypes": activityRaidHash,
                "completions": 2,
                "points": 1
            },

            "Finish three dungeons": {
                "requirements": ["allowedTypes", "completions"],
                "allowedTypes": activityDungeonHash,
                "completions": 3,
                "points": 1
            }
        },

        # experienced players
        "Experienced Players": {
            "Do a raid with a specific loadout": {
                "requirements": ["allowedTypes", "customLoadout"],
                "allowedTypes": activityRaidHash,
                "extraText": "\n⁣\nKinetic: ? \n Energy: % \n Power: & ",
                "points": 1
            },

            "Do a dungeon with a specific loadout": {
                "requirements": ["allowedTypes", "customLoadout"],
                "allowedTypes": activityDungeonHash,
                "extraText": "\n⁣\nKinetic: ? \n Energy: % \n Power: & ",
                "points": 1
            },

            "Finish a raid within the allowed time frame": {
                "requirements": ["allowedTypes", "speedrun"],
                "extraText": "",
                "points": 1
            },

            "Finish a raid with 20 power or more below recommended (only you have to be lower light)": {
                "requirements": ["allowedTypes", "contest"],
                "allowedTypes": activityRaidHash,
                "contest": 20,
                "points": 1
            },

            "Do a flawless raid (only you don't have to die)": {
                "requirements": ["allowedTypes", "totalDeaths"],
                "allowedTypes": activityRaidHash,
                "totalDeaths": 0,
                "points": 1
            },

            "Do a flawless dungeon (only you don't have to die)": {
                "requirements": ["allowedTypes", "totalDeaths"],
                "allowedTypes": activityDungeonHash,
                "totalDeaths": 0,
                "points": 1
            }
        }
    },


    # general pve bounties
    'PvE': {
        # new players
        "New Players": {
            "Finish a strike with high kills (100) and low deaths (1)": {
                "requirements": ["allowedTypes", "totalKills", "totalDeaths"],
                "allowedTypes": activityStrikeAndNFHash,
                "totalDeaths": 1,
                "totalKills": 100,
                "points": 1
            },

            "Clear an adventure with a specific loadout": {
                "requirements": ["allowedTypes", "customLoadout"],
                "allowedTypes": activityStoryHash,
                "extraText": "\n⁣\nKinetic: ? \n Energy: % \n Power: & ",
                "points": 1
            },

            "Complete a Nightfall: The Ordeal on any difficulty": {
                "requirements": ["allowedTypes"],
                "allowedTypes": activityNFHash,
                "points": 1
            }
        },

        # experienced players
        "Experienced Players": {
            "Finish a strike with high kills (100) and low deaths (0) in under 10 minutes": {
                "requirements": ["allowedTypes", "speedrun", "totalKills", "totalDeaths"],
                "allowedTypes": activityStrikeAndNFHash,
                "speedrun": 600,
                "totalDeaths": 0,
                "totalKills": 100,
                "points": 1
            },

            # todo not implemented yet bc BL will probly change everything here
            #
            # "Clear this daily heroic adventure within the allowed time frame": {
            # },

            "Complete a Nightfall: The Ordeal with a high score (150k)": {
                "requirements": ["allowedTypes", "NFscore"],
                "allowedTypes": activityNFHash,
                "NFscore": 150_000,
                "points": 1
            }
        }
    },


    # pvp bounties
    'PvP': {
        # new players
        "New Players": {
            "Win a crucible game with a positive K/D": {
                "requirements": ["allowedTypes", "win", "kd"],
                "allowedTypes": activityPVPHash,
                "kd": 1,
                "points": 1
            },

            "Get a win streak of 3 the crucible": {
                "requirements": ["allowedTypes", "winStreak"],
                "allowedTypes": activityPVPHash,
                "winStreak": 3,
                "points": 1
            }
        },

        # experienced players
        "Experienced Players": {
            "Get a win streak of 5 the crucible": {
                "requirements": ["allowedTypes", "winStreak"],
                "allowedTypes": activityPVPHash,
                "winStreak": 5,
                "points": 1
            },

            "Win a crucible game with a K/D > 3": {
                "requirements": ["allowedTypes", "win", "kd"],
                "allowedTypes": activityPVPHash,
                "kd": 3,
                "points": 1
            },

            "Win a crucible game with a high amount of kills (30)": {
                "requirements": ["allowedTypes", "win", "totalKills"],
                "allowedTypes": activityPVPHash,
                "totalKills": 30,
                "points": 1
            },

            "Win a crucible game without dying": {
                "requirements": ["allowedTypes", "win", "totalDeaths"],
                "allowedTypes": activityPVPHash,
                "totalDeaths": 0,
                "points": 1
            }
        }
    }
}

# ----------------------------------------------------------------------
# bounties where the whole clan competes against each other
competition_bounties = {
    # raid bounties
    'Raids': {
        "Get the fastest clear of the raid __?__": {
            "requirements": ["randomActivity", "speedrun"],
            "randomActivity": raidHashes,
            "extraText": "",
            "points": 1
        },

        "Get the fastest clear of the dungeon __?__": {
            "requirements": ["randomActivity", "speedrun"],
            "randomActivity": dungeonHashes,
            "extraText": "",
            "points": 1
        },

        "Do a lowman (solo, duo or trio) of __?__": {
            "requirements": ["randomActivity", "lowman"],
            "randomActivity": raidHashes,
            "extraText": "",
            "points": [3, 2, 1]             # [solo, duo, trio] todo
        },

        "Get the fastest clear of the raid __?__ while everyone uses abilities only": {
            "requirements": ["randomActivity", "speedrun", "noWeapons"],
            "randomActivity": raidHashes,
            "extraText": "",
            "points": 1
        },
    },

    # general pve bounties
    'PvE': {
        # todo not implemented yet bc BL will probly change everything here
        #
        # "Get the fastest completion of this daily heroic story mission": {
        # },

        "Get the most kills in a gambit match": {
            "requirements": ["allowedTypes", "totalKills"],
            "allowedTypes": activityGambitHash,
            "points": 0
        },

        "Get the highest Nightfall Score": {
            "requirements": ["allowedTypes", "NFscore"],
            "allowedTypes": activityNFHash,
            "points": 0
        }
    },

    # pvp bounties
    'PvP': {
        "Get the highest kills in a game in any PvP mode": {
            "requirements": ["allowedTypes", "totalKills"],
            "allowedTypes": activityPVPHash,
            "points": 0
        },

        "Get the best K/D in a game in any PvP mode": {
            "requirements": ["allowedTypes", "kd"],
            "allowedTypes": activityPVPHash,
            "points": 0
        },

        "Go Flawless and visit the Lighthouse": {
            "requirements": ["allowedTypes"],
            "allowedTypes": activityLighthouseHash,
            "points": 0
        },

        "Win this weeks PvP tournament": {
            "requirements": ["tournament"],
            "points": 0
        }
    }
}
