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
allowedActivities   #todo
allowedTypes        # which activity type hashes are allow, fe. activityTypeHash: 1686739444 is story
speedrun            #todo
lowman              #todo
contest             #todo
completions         #todo
firstClear          #todo
noWeapons           #todo
customLoadout       #todo
kd                  #todo
totalKills          #todo
totalDeaths         #todo
NFscore             #todo
win                 #todo
winStreak           #todo
tournament          #todo

extra_text          # will show more text
points              # how many points the user gets for completing the bounty

"""

""" Hashes:"""
from static.dict import *

bounties = {
    # raid bounties
    'Raids': {
        # new players
        "New Players": {
            "Clear a raid for the first time": {
                "requirements": ["allowedTypes", "firstClear"],
                "points": 0
            },

            "Finish two raids": {
                "requirements": ["allowedTypes", "completions"],
                "allowedTypes": activityRaidHash,
                "points": 0
            },

            "Finish two dungeons": {
                "requirements": ["allowedTypes", "completions"],
                "allowedTypes": activityDungeonHash,
                "points": 0
            }
        },

        # experienced players
        "Experienced Players": {
            "Do a raid with a specific loadout": {
                "requirements": ["allowedTypes", "completions", "customLoadout"],
                "allowedTypes": activityRaidHash,
                "extraText": "Kinetic: % \n Energy: % \n Power: % ",
                "points": 0
            },

            "Do a dungeon with a specific loadout": {
                "requirements": ["allowedTypes", "completions", "customLoadout"],
                "allowedTypes": activityDungeonHash,
                "extraText": "Kinetic: % \n Energy: % \n Power: % ",
                "points": 0
            },

            "Finish a raid within the allowed time frame": {
                "requirements": ["allowedTypes", "completions", "speedrun"],
                "extraText": "",
                "points": 0
            },

            "Finish a raid with 20 power or more below recommended": {
                "requirements": ["allowedTypes", "completions", "contest"],
                "allowedTypes": activityRaidHash,
                "points": 0
            },

            "Do a flawless raid (only you don't have to die)": {
                "requirements": ["allowedTypes", "completions", "totalDeaths"],
                "allowedTypes": activityRaidHash,
                "points": 0
            },

            "Do a flawless dungeon (only you don't have to die)": {
                "requirements": ["allowedTypes", "completions", "totalDeaths"],
                "allowedTypes": activityDungeonHash,
                "points": 0
            }
        }
    },


    # general pve bounties
    'PvE': {
        # new players
        "New Player": {
            "Finish a strike with high kills and low deaths": {
                "requirements": ["allowedTypes", "completions", "totalKills", "totalDeaths"],
                "allowedTypes": activityStrikeAndNFHash,
                "points": 0
            },

            "Clear an adventure with a specific loadout": {
                "requirements": ["allowedTypes", "completions", "customLoadout"],
                "allowedTypes": activityStoryHash,
                "extraText": "Kinetic: % \n Energy: % \n Power: % ",
                "points": 0
            },

            "Complete a Nightfall: The Ordeal on any difficulty": {
                "requirements": ["allowedTypes", "completions"],
                "allowedTypes": activityNFHash,
                "points": 0
            }
        },

        # experienced players
        "Experienced Players": {
            "Finish a strike with high kills and low deaths": {
                "requirements": ["allowedTypes",  "completions", "totalKills", "totalDeaths"],
                "allowedTypes": activityStrikeAndNFHash,
                "points": 0
            },

            # todo not implemented yet bc BL will probly change everything here
            #
            # "Clear this daily heroic adventure within the allowed time frame": {
            # },

            "Complete a Nightfall: The Ordeal with a high score": {
                "requirements": ["allowedTypes", "completions", "NFscore"],
                "allowedTypes": activityNFHash,
                "points": 0
            }
        }
    },


    # pvp bounties
    'PvP': {
        # new players
        "New Player": {
            "Win a crucible game with a positive K/D": {
                "requirements": ["allowedTypes", "win", "kd"],
                "allowedTypes": activityPVPHash,
                "points": 0
            },

            "Get a win streak of 3 the crucible": {
                "requirements": ["allowedTypes", "winStreak"],
                "allowedTypes": activityPVPHash,
                "points": 0
            }
        },

        # experienced players
        "Experienced Players": {
            "Get a win streak of 5 the crucible": {
                "requirements": ["allowedTypes", "winStreak"],
                "allowedTypes": activityPVPHash,
                "points": 0
            },

            "Win a crucible game with a K/D > 3": {
                "requirements": ["allowedTypes", "win", "kd"],
                "allowedTypes": activityPVPHash,
                "points": 0
            },

            "Win a crucible game with a high amount of kills": {
                "requirements": ["allowedTypes", "win", "totalKills"],
                "allowedTypes": activityPVPHash,
                "points": 0
            },

            "Win a crucible game without dying": {
                "requirements": ["allowedTypes", "win", "totalDeaths"],
                "allowedTypes": activityPVPHash,
                "points": 0
            }
        }
    }
}


# bounties where the whole clan competes against each other
competition_bounties = {
    # raid bounties
    'Raids': {
        "Get the fastest clear of the raid __?__": {
            "requirements": ["randomActivity", "speedrun"],
            "randomActivity": raidHashes,
            "extraText": "",
            "points": 0
        },

        "Get the fastest clear of the dungeon __?__": {
            "requirements": ["randomActivity", "speedrun"],
            "randomActivity": dungeonHashes,
            "extraText": "",
            "points": 0
        },

        "Do a lowman (solo, duo or trio) of __?__": {
            "requirements": ["randomActivity", "lowman"],
            "randomActivity": raidHashes,
            "extraText": "",
            "points": [0, 0, 0]             # [solo, duo, trio]
        },

        "Get the fastest clear of the raid __?__ while everyone uses abilities only": {
            "requirements": ["randomActivity", "speedrun", "noWeapons"],
            "randomActivity": raidHashes,
            "extraText": "",
            "points": 0
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
