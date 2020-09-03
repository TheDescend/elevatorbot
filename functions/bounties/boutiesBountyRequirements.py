"""
Template:

"Description": {
    "requirements": ["a", "b"],     # what requirements does the role have
    "a": ...,                       # details on the requirement
    "b": ...
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



bounties = {
    # raid bounties
    'Raids': {
        # new players
        "New Players": {
            "Clear a raid for the first time": {
                "requirements": [""],

            },

            "Finish two raids": {

            },

            "Finish two dungeons": {

            }
        },

        # experienced players
        "Experienced Players": {
            "Do a raid with this loadout": {

            },

            "Do a dungeon with this loadout": {

            },

            "Finish a raid within the allowed time frame": {

            },

            "Finish a raid with 20 power or more below recommended": {

            },

            "Do a flawless raid": {

            },

            "Do a flawless dungeon": {

            }
        }
    },


    # general pve bounties
    'PvE': {
        # new players
        "New Player": {
            "Finish a strike with high kills and low deaths": {

            },

            "Clear an adventure with this loadout": {

            },

            "Complete a Nightfall: The Ordeal on any difficulty": {

            }
        },

        # experienced players
        "Experienced Players": {
            "Finish a strike with high kills and low deaths": {

            },

            # todo not implemented yet bc BL will probly change everything here
            #
            # "Clear this daily heroic adventure within the allowed time frame": {
            #     "requirements": ["randomActivity"],
            #     "randomActivity": dailyHeroicHashes
            # },

            "Complete a Nightfall: The Ordeal with a high score": {

            }
        }
    },


    # pvp bounties
    'PvP': {
        # new players
        "New Player": {
            "Win a crucible game with a positive K/D": {

            },

            "Get a win streak in the crucible": {

            }
        },

        # experienced players
        "Experienced Players": {
            "Get a win streak in the crucible": {

            },

            "Win a crucible game with a high K/D": {

            },

            "Complete a crucible game with a high amount of kills": {

            },

            "Complete a crucible game without dying": {

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
            "randomActivity": raidHashes
        },

        "Get the fastest clear of this dungeon": {
            "requirements": ["randomActivity"],
            "randomActivity": dungeonHashes
        },

        "Do a lowman of this raid": {
            "requirements": ["randomActivity"],
            "randomActivity": raidHashes
        },

        "Get the fastest clear of this raid while using abilities only": {
            "requirements": ["randomActivity"],
            "randomActivity": raidHashes
        },
    },

    # general pve bounties
    'PvE': {
        # todo not implemented yet bc BL will probly change everything here
        #
        # "Get the fastest completion of this daily heroic story mission": {
        #     "requirements": ["randomActivity"],
        #     "randomActivity": dailyHeroicHashes
        # },

        "Get the most kills in a gambit match": {

        },

        "Get the highest Nightfall Score": {

        }
    },

    # pvp bounties
    'PvP': {
        "Get the highest kills in any PvP mode": {

        },

        "Get the best K/D in any PvP mode": {

        },

        "Go Flawless and visit the Lighthouse": {

        },

        "Win this weeks PvP tournament": {

        }
    }
}
