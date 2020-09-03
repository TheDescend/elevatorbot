"""
Template:

"Description": {
    "requirements": ["a", "b"],     # what requirements does the role have
    "a": ...,                       # details on the requirement
    "b": ...,

    "points": integer               # how many points the completion / win gives
}


Current requirements:

randomActivity      # one value will automatically get changed to allowedActivities during selection process
allowedActivities   #todo
allowedTypes        # which activity type hashes are allow, fe. activityTypeHash: 1686739444 is story
speedrun            #todo
contest             #todo
completions         #todo
firstClear          #todo
customLoadout       #todo
kd                  #todo
totalKills          #todo
totalDeaths         #todo
NFscore             #todo
winStreak           #todo

points              # how many points the user gets for completing the bounty

"""

""" Hashes:"""
from static.dict import *

# only activities which are available are included here
raidHashes = lwHashes + gosHashes
dungeonHashes = throneHashes + pitHashes + prophHashes

ActivityStrikeAndNFHash = ActivityNFHash + ActivityStrikeHash



bounties = {
    # raid bounties
    'Raids': {
        # new players
        "New Players": {
            "Clear a raid for the first time": {

                "points": 0
            },

            "Finish two raids": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityRaidHash,
                "points": 0
            },

            "Finish two dungeons": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityDungeonHash,
                "points": 0
            }
        },

        # experienced players
        "Experienced Players": {
            "Do a raid with this loadout": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityRaidHash,
                "points": 0
            },

            "Do a dungeon with this loadout": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityDungeonHash,
                "points": 0
            },

            "Finish a raid within the allowed time frame": {

                "points": 0
            },

            "Finish a raid with 20 power or more below recommended": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityRaidHash,
                "points": 0
            },

            "Do a flawless raid": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityRaidHash,
                "points": 0
            },

            "Do a flawless dungeon": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityDungeonHash,
                "points": 0
            }
        }
    },


    # general pve bounties
    'PvE': {
        # new players
        "New Player": {
            "Finish a strike with high kills and low deaths": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityStrikeAndNFHash,
                "points": 0
            },

            "Clear an adventure with this loadout": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityStoryHash,
                "points": 0
            },

            "Complete a Nightfall: The Ordeal on any difficulty": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityNFHash,
                "points": 0
            }
        },

        # experienced players
        "Experienced Players": {
            "Finish a strike with high kills and low deaths": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityStrikeAndNFHash,
                "points": 0
            },

            # todo not implemented yet bc BL will probly change everything here
            #
            # "Clear this daily heroic adventure within the allowed time frame": {
            #     "requirements": ["randomActivity"],
            #     "randomActivity": dailyHeroicHashes,
            #     "points": 0
            # },

            "Complete a Nightfall: The Ordeal with a high score": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityNFHash,
                "points": 0
            }
        }
    },


    # pvp bounties
    'PvP': {
        # new players
        "New Player": {
            "Win a crucible game with a positive K/D": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityPVPHash,
                "points": 0
            },

            "Get a win streak in the crucible": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityPVPHash,
                "points": 0
            }
        },

        # experienced players
        "Experienced Players": {
            "Get a win streak in the crucible": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityPVPHash,
                "points": 0
            },

            "Win a crucible game with a high K/D": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityPVPHash,
                "points": 0
            },

            "Complete a crucible game with a high amount of kills": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityPVPHash,
                "points": 0
            },

            "Complete a crucible game without dying": {
                "requirements": ["allowedTypes"],
                "allowedTypes": ActivityPVPHash,
                "points": 0
            }
        }
    }
}


# bounties where the whole clan competes against each other
competition_bounties = {
    # raid bounties
    'Raids': {
        "Get the fastest clear of this raid": {
            "requirements": ["randomActivity"],
            "randomActivity": raidHashes,
            "points": 0
        },

        "Get the fastest clear of this dungeon": {
            "requirements": ["randomActivity"],
            "randomActivity": dungeonHashes,
            "points": 0
        },

        "Do a lowman of this raid": {
            "requirements": ["randomActivity"],
            "randomActivity": raidHashes,
            "points": 0
        },

        "Get the fastest clear of this raid while using abilities only": {
            "requirements": ["randomActivity"],
            "randomActivity": raidHashes,
            "points": 0
        },
    },

    # general pve bounties
    'PvE': {
        # todo not implemented yet bc BL will probly change everything here
        #
        # "Get the fastest completion of this daily heroic story mission": {
        #     "requirements": ["randomActivity"],
        #     "randomActivity": dailyHeroicHashes,
        #     "points": 0
        # },

        "Get the most kills in a gambit match": {
            "requirements": ["allowedTypes"],
            "allowedTypes": ActivityGambitHash,
            "points": 0
        },

        "Get the highest Nightfall Score": {
            "requirements": ["allowedTypes"],
            "allowedTypes": ActivityNFHash,
            "points": 0
        }
    },

    # pvp bounties
    'PvP': {
        "Get the highest kills in any PvP mode": {
            "requirements": ["allowedTypes"],
            "allowedTypes": ActivityPVPHash,
            "points": 0
        },

        "Get the best K/D in any PvP mode": {
            "requirements": ["allowedTypes"],
            "allowedTypes": ActivityPVPHash,
            "points": 0
        },

        "Go Flawless and visit the Lighthouse": {
            "requirements": ["allowedTypes"],
            "allowedTypes": ActivityLighthouseHash,
            "points": 0
        },

        "Win this weeks PvP tournament": {

            "points": 0
        }
    }
}
