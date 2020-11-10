getNameFromHashRecords = {}
getNameFromHashActivity= {}
getNameFromHashCollectible = {}
getNameFromHashInventoryItem = {}



# from https://data.destinysets.com/
# raids
spirePHashes = [3213556450]
spireHashes = [119944200]
eaterPHashes = [809170886]
eaterHashes = [3089205900]
#there is a hash for each levi-rotation and one for each possible prestige modifier
leviHashes = [2693136600, 2693136601, 2693136602, 2693136603, 2693136604, 2693136605]
leviPHashes = [417231112, 508802457, 757116822, 771164842, 1685065161, 1800508819, 2449714930, 3446541099, 3857338478, 3879860661, 3912437239, 4206123728]
scourgeHashes = [548750096] 
lwHashes = [2122313384]
cosHashes = [3333172150, 960175301] 
gosHashes = [3845997235, 2659723068]

# dungeons
throneHashes = [1893059148, 2032534090]
pitHashes = [1375089621, 2559374368, 2559374374, 2559374375]
prophHashes = [4148187374]

# menagerie
premenHashes = [2509539864, 2509539865, 2509539867, 1831470693, 3107795800, 3115455134]

# secret missions
zeroHashes = [3232506937] 
herzeroHashes = [2731208666]

# daily heroic missions - empty for now, since most stuff wil get deleted in BL
# heroicStoryHashes =



#activityTypeHashes
activityStoryHash = [147238405, 1686739444, 1299744814, 2201105581, 2911768360]
activityRaidHash = [2043403989]
activityDungeonHash = [608898761]
activityGambitHash = [636666746, 1418469392, 2490937569]    # will probly change with BL
activityNFHash = [575572995]
activityStrikeHash = [2884569138, 2884569138, 4110605575, 4110605575, 4164571395]
activityPrivateMatchHash = [4260058063]
activityPVPHash = [96396597, 158362448, 517828061, 964120289, 1434366740, 1472571612, 1522227381, 2112637710,
                   2175955486, 2278747016, 2371050408, 2394267841, 2410913661, 2505748283, 3252144427, 3268478079,
                   3517186939, 3610972626, 3954711135, 3956087078, 3956381302, 3990775146, 4141415314, 4288302346]
activityLighthouseHash = [4276116472]


# Metric hashes
metricLeviCompletions = [2486745106]
metricEoWCompletions = [2659534585]
metricSosCompletions = [700051716]
metricLWCompletions = [905240985]
metricScourgeCompletions = [1201631538]
metricCoSCompletions = [1815425870]
metricGoSCompletions = [1168279855]

metricRaidAllocation = {
    tuple(eaterHashes): metricEoWCompletions,
    tuple(spireHashes): metricSosCompletions,
    tuple(scourgeHashes): metricScourgeCompletions,
    tuple(cosHashes): metricCoSCompletions,
    tuple(lwHashes): metricLWCompletions,
    tuple(gosHashes): metricGoSCompletions,
}

metricWinStreakGambitWeekly = [1053579811]
metricWinStreakCrucibleWeekly = [4044111774]

metricWinStreakWeeklyAllocation = {
    tuple(activityGambitHash): metricWinStreakGambitWeekly,
    tuple(activityPVPHash): metricWinStreakCrucibleWeekly
}



""" Grouped Hashes """
# only activities which are available should be included here
availableRaidHashes = [lwHashes, gosHashes]
raidHashes = availableRaidHashes + [leviHashes, leviPHashes, eaterHashes, eaterPHashes, spireHashes, spirePHashes, scourgeHashes, cosHashes]
availableDungeonHashes = [throneHashes, pitHashes, prophHashes]

activityStrikeAndNFHash = activityNFHash + activityStrikeHash

metricAvailableRaidCompletion = metricLWCompletions + metricGoSCompletions
metricRaidCompletion = metricAvailableRaidCompletion + metricLeviCompletions + metricEoWCompletions + metricSosCompletions + metricScourgeCompletions + metricCoSCompletions



"""" Speedrun Times: 2x WR for now https://www.speedrun.com/destiny2"""
# has to be tuples bc lists are not hashable
speedrunActivitiesRaids = {
    tuple(scourgeHashes): 648,             # scourge
    tuple(cosHashes): 1118,                # cos
    tuple(lwHashes): 720,                  # lw doesn't have a time, so 12mins it is
    tuple(gosHashes): 1496,                # gos
}
# consists of all of them
speedrunActivities = speedrunActivitiesRaids




""" Weapon Hashes """
damageTypeKinetic = 3373582085
damageTypeSolar = 1847026933
damageTypeVoid = 3454344768
damageTypeArc = 2303181850

weaponTypeKinetic = 1498876634
weaponTypeEnergy = 2465295065
weaponTypePower = 953998645

possibleWeaponsKinetic = ["Hand Cannon", "Scout Rifle", "Auto Rifle", "Pulse Rifle", "Sidearm", "Submachine Gun", "Combat Bow", "Sniper Rifle", "Shotgun", "Grenade Launcher"]
possibleWeaponsEnergy = ["Hand Cannon", "Scout Rifle", "Auto Rifle", "Pulse Rifle", "Sidearm", "Fusion Rifle", "Shotgun", "Sniper Rifle", "Trace Rifle", "Grenade Launcher", "Combat Bow"]
possibleWeaponsPower = ["Grenade Launcher", "Rocket Launcher", "Linear Fusion Rifle", "Sword", "Shotgun", "Machine Gun", "Sniper Rifle"]





clanids = {
    4107840 : 'The Descend'
}

discord_channels = {
    'general': 670400011519000616,
    'media' : 670400027155365929,
    'spoilerchat': 670402166103474190,
    'offtopic': 670362162660900895
}

requirementHashes = {
    'Y1':{
        'Spire of Stars': {
            "deprecated": True,
            'requirements': ['clears'],
            'clears': [
                {'count' : 4,
                'actHashes' : spireHashes + spirePHashes}, #normal
            ],
            'replaced_by': ['Spire of Stars Master', 'Y1 Raid Master']
        },
        'Spire of Stars Master': {
            "deprecated": True,
            'requirements': ['clears','flawless'],
            'clears': [
                {'count' : 10,
                'actHashes' : spirePHashes}  #prestige
            ],
            'flawless' : spireHashes + spirePHashes,
            'replaced_by': ['Y1 Raid Master']
        },
        'Eater of Worlds': {
            "deprecated": True,
            'requirements': ['clears'],
            'clears': [
                {'count' : 4,
                'actHashes' : eaterHashes + eaterPHashes}, #normal
            ],
            'replaced_by':['Eater of Worlds Master', 'Y1 Raid Master']
        },
        'Eater of Worlds Master': {
            "deprecated": True,
            'requirements': ['clears','flawless'],
            'clears': [
                {'count' : 10,
                'actHashes' : eaterPHashes}
            ], #prestige
            'flawless': eaterHashes + eaterPHashes,
            'replaced_by': ['Y1 Raid Master']
        },
        'Leviathan': {
            "deprecated": True,
            'requirements': ['clears'],
            'clears': [
                {'count' : 4,
                'actHashes' : leviHashes + leviPHashes}, #normal
            ],
            'replaced_by': ['Leviathan Master', 'Y1 Raid Master']
        },
        'Leviathan Master': {
            "deprecated": True,
            'requirements': ['clears','flawless','collectibles'],
            'clears':[
                {'count' : 10,
                'actHashes' : leviPHashes}, #prestige
            ],
            'flawless': leviHashes + leviPHashes,
            'collectibles': [
                3125541834, #1766893932, #good dog
                3125541835, #1766893933, #splish splash
                3125541833, #1766893935, #two enter, one leaves
                3125541832  #1766893934  #take the throne
            ],
            'replaced_by': ['Y1 Raid Master']
        },
        'Y1 Raid Master': {
            "deprecated": True,
            'requirements': ['roles'],
            'roles':[
                'Spire of Stars Master',
                'Eater of Worlds Master',
                'Leviathan Master'
            ]
        }
    },
    'Y2':{
        'Crown of Sorrow': {
            "deprecated": True,
            'requirements': ['clears','records'],
            'clears':[
                {'count' : 15,
                'actHashes' : cosHashes}
            ], #• Minimum 15 full clears
            'records': [
                1575460004,    #Limited Blessings
                1575460003,    #Total Victory
                1575460002,    #With Both Hands
           ],
           'replaced_by': ['Y2 Raid Master', 'Crown of Sorrow Master']
       },
        'Crown of Sorrow Master': {
            "deprecated": True,
            'requirements': ['clears','records'],
            'clears': [
                {'count' : 30,
                'actHashes' : cosHashes} #Minimum 15 full clears
            ],
            'records': [
                1558682416,    #Crown of Ease [Flawless]
                1558682417,    #Arc Borne :Arc: 
                1558682418,    #Void Borne :Void: 
                1558682419,    #Solar Borne :Solar: 
                1558682428    #Stay Classy [Same Class]
            ],
            'replaced_by':['Y2 Raid Master']
        },
        'Scourge of the Past': {
            "deprecated": True,
            'requirements': ['clears','records'],
            'clears': [
                {'count' : 15,
                'actHashes' : scourgeHashes}
            ],
            'records':[
                1428463716,    #All For One, One For All
                1804999028,    #Hold the Line
                4162926221,    #To Each Their Own
            ],
            'replaced_by':['Y2 Raid Master', 'Scourge of the Past Master']
        },
        'Scourge of the Past Master': {
            "deprecated": True,
            'requirements': ['clears','records'],
            'clears': [
                {'count' : 30,
                'actHashes' : scourgeHashes}
            ],
            'records': [
                2648109757,    #Like a Diamond
                772878705,     #Solarstruck
                496309570,     #Voidstruck
                105811740,     #Thunderstruck
                3780682732,    #Stay Classy
            ],
            'replaced_by':['Y2 Raid Master']
        },
        'Last Wish': {
            'requirements': ['clears','records'],
            'clears': [
                {'count' : 15,
                'actHashes' : lwHashes},   #Minimum 15 full clears
            ],
            'records':[
                2822000740,    #Summoning Ritual
                2196415799,    #Coliseum Champion
                1672792871,    #Forever Fight
                149192209,     #Keep Out
                3899933775    #Strength of Memory
            ],
            'replaced_by':['Y2 Raid Master', 'Last Wish Master']
        },
        'Last Wish Master': {
            'requirements': ['clears','records'],
            'clears': [
                {'count' : 30,
                'actHashes' : lwHashes}
            ], #Minimum 15 full clears
            'records': [
                4177910003,    #Petra's Run [Flawless]
                3806804934,    #Thunderstruck :Arc:
                567795114,     #The New Meta [Same Class]
                1373122528,    #Night Owl :Void:
                2398356743    #Sunburn :Solar:
            ],
            'replaced_by':['Y2 Raid Master']
        },
        'Y2 Raid Master': {
            'requirements': ['roles'],
            'roles':[
                'Last Wish Master',
                'Scourge of the Past Master',
                'Crown of Sorrow Master'
            ]
        }
    },
    'Y3':{
        'Garden of Salvation': {
            'requirements': ['clears','records'],
            'clears':[
                {'count' : 15,
                'actHashes' : gosHashes} #Minimum 15 full clears
            ], 
            'records': [
                3281243931, #Leftovers
                1925300422, #A Link to the Chain
                1661612473, #To the Top
                3167166053, #Zero to One Hundred
            ],
            'replaced_by':['Y3 Raid Master']
       },
        'Y3 Raid Master': {
            'requirements': ['clears', 'records'],
            'clears': [
                {'count' : 30,
                'actHashes' : gosHashes} #Minimum 30 full clears
            ],
            'records': [
                3144827156, #Inherent Perfection [Flawless]
                2841179989, #Fluorescent Foliage :Arc: 
                4019629605, #Shade in the Garden :Void: 
                3382024472, #Photosynthesis :Solar: 
                4025379205, #Garden Party [Same Class]
            ]
        }
    },
    'Dungeons': {
        'Solo Flawless Shattered Throne': {
            'requirements': ['records'],
            'denyTime0':{ #start is earlier Time, format is important
                'startTime':'11/08/2020 18:00',
                'endTime':'08/09/2020 18:00'
            },
             'records': [
                1290451257, #Solo Flawless Shattered Throne
            ]
        },
        'Flawless Shattered Throne': {
            'requirements': ['records'],
            'records': [
                2029263931, #Flawless Shattered Throne
            ],
            'replaced_by':['Solo Flawless Shattered Throne']
        },
        'Solo Shattered Throne': {
            'requirements': ['records'],
            'denyTime0':{ #start is earlier Time, format is important
                'startTime':'11/08/2020 18:00',
                'endTime':'08/09/2020 18:00'
            },
            'records': [
                851701008, #Solo Shattered Throne
            ],
            'replaced_by':['Solo Flawless Shattered Throne']
        },
        'Solo Flawless Pit of Heresy': {
            'requirements': ['records'],
            'denyTime0':{ #start is earlier Time, format is important
                'startTime':'11/08/2020 18:00',
                'endTime':'08/09/2020 18:00'
            },
            'records': {
                2615277024,  # Savior of the Deep
            },
        },
        'Solo Pit of Heresy': {
            'requirements': ['records'],
            'denyTime0':{ #start is earlier Time, format is important
                'startTime':'11/08/2020 18:00',
                'endTime':'08/09/2020 18:00'
            },
            'records': {
                376114010,  # Usurper
            },
            'replaced_by': ['Solo Flawless Pit of Heresy']
        },
        'Flawless Pit of Heresy': {
            'requirements': ['records'],
            'records': {
                3279886460,  # Eternal Heretic
            },
            'replaced_by': ['Solo Flawless Pit of Heresy']
        },
        'Solo Prophecy': {
            'requirements': ['records'],
            'records' : [
                2382088899
            ],
            'replaced_by': ['Solo Flawless Prophecy']
        },
        'Flawless Prophecy': {
            'requirements': ['records'],
            'records' : [
                2094467183
            ],
            'replaced_by': ['Solo Flawless Prophecy']
        },
        'Solo Flawless Prophecy': {
            'requirements': ['records'],
            'records' : [
                3931440391
            ],
        }
    },
    "Lowmans":{
        'Three-Man Argos': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount' : 3,
            'activityHashes': eaterHashes + eaterPHashes,
            'replaced_by': ['Solo Argos', 'Two-Man Argos'],
         },
        'Two-Man Argos': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount' : 2,
            'activityHashes': eaterHashes + eaterPHashes,
            'replaced_by': ['Solo Argos'],
         },
        'Solo Argos': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount' : 1,
            'activityHashes': eaterHashes + eaterPHashes,
         },
        'Three-Man Insurrection': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount' : 3,
            'activityHashes': scourgeHashes,
            'replaced_by': ['Two-Man Insurrection'],
         },
        'Two-Man Insurrection': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount' : 2,
            'activityHashes': scourgeHashes,
         },
         'Solo Queenswalk': {
            'requirements': ['lowman'],
            'playercount' : 1,
            'activityHashes': lwHashes
         },
         'Two-Man Queenswalk': {
            'requirements': ['lowman'],
            'playercount' : 2,
            'activityHashes': lwHashes,
            'replaced_by': ['Solo Queenswalk']
         },
         'Three-Man Queenswalk': {
            'requirements': ['lowman'],
            'playercount' : 3,
            'activityHashes': lwHashes,
            'replaced_by': ['Solo Queenswalk', 'Two-Man Queenswalk']
         },
         'Two-Man Calus': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount' : 2,
            'activityHashes': leviHashes + leviPHashes,
         },
         'Three-Man Gahlran': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount' : 3,
            'activityHashes': cosHashes,
            'replaced_by': ['Two-Man Gahlran'],
         },
         'Two-Man Gahlran': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount' : 2,
            'activityHashes': cosHashes,
         },
         'Two-Man Sanctified Mind': {
            'requirements': ['lowman'],
            'playercount' : 2,
            'activityHashes': gosHashes,
         },
        'Three-Man Sanctified Mind': {
            'requirements': ['lowman'],
            'playercount' : 3,
            'activityHashes': gosHashes,
            'replaced_by': ['Two-Man Sanctified Mind'],
         },
        'Three-Man Heroic Menagerie': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount' : 3,
            'activityHashes': premenHashes,
            'replaced_by': ['Two-Man Heroic Menagerie', 'Solo Heroic Menagerie']
        },
        'Two-Man Heroic Menagerie': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount' : 2,
            'activityHashes': premenHashes,
            'replaced_by': ['Solo Heroic Menagerie']
        },
        'Solo Heroic Menagerie': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount' : 1,
            'activityHashes': premenHashes
        }
    },
    'Addition':{
        'Niobe\'s Torment': {
            "deprecated": True,
            'requirements': ['collectibles'],
            'collectibles': [
                3531075476, #Armory Forged Shell
            ]
        },
        'The Other Side': {
            "deprecated": True,
            'requirements': ['records'],
            'denyTime0':{ #start is earlier Time, format is important
                'startTime':'11/08/2020 18:00',
                'endTime':'08/09/2020 18:00'
            },
            'records': [
                807845972, #Only the essentials
            ]
        },
        'Solo Zero Hour': {
            "deprecated": True,
            'requirements': ['lowman'],
            'denyTime0':{ #start is earlier Time, format is important
                'startTime':'10/03/2020 18:00',
                'endTime':'21/04/2020 18:00'
            },
            'denyTime1':{ #start is earlier Time, format is important
                'startTime':'11/08/2020 18:00',
                'endTime':'08/09/2020 18:00'
            },
            'playercount' : 1,
            'activityHashes': zeroHashes,
            'replaced_by': ['Solo Flawless Zero Hour']
        },
        'Solo Heroic Zero Hour': {
            "deprecated": True,
            'requirements': ['lowman'],
            'denyTime0':{ #start is earlier Time, format is important
                'startTime':'10/03/2020 18:00',
                'endTime':'21/04/2020 18:00'
            },
            'denyTime1':{ #start is earlier Time, format is important
                'startTime':'11/08/2020 18:00',
                'endTime':'08/09/2020 18:00'
            },
            'playercount' : 1,
            'activityHashes': herzeroHashes,
            'replaced_by': ['Solo Flawless Heroic Zero Hour']
        },
        'Solo Flawless Zero Hour': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount' : 1,
            'denyTime0':{ #start is earlier Time, format is important
                'startTime':'10/03/2020 18:00',
                'endTime':'21/04/2020 18:00'
            },
            'denyTime1':{ #start is earlier Time, format is important
                'startTime':'11/08/2020 18:00',
                'endTime':'08/09/2020 18:00'
            },
            'flawless' : True,
            'activityHashes': zeroHashes
        },
        'Solo Flawless Heroic Zero Hour': {
            "deprecated": True,
            'requirements': ['lowman'],
            'denyTime0':{ #start is earlier Time, format is important
                'startTime':'10/03/2020 18:00',
                'endTime':'21/04/2020 18:00'
            },
            'denyTime1':{ #start is earlier Time, format is important
                'startTime':'11/08/2020 18:00',
                'endTime':'08/09/2020 18:00'
            },
            'playercount' : 1,
            'flawless' : True,
            'activityHashes': herzeroHashes
        },


        #'Name': {
        #    'requirements': ['collectibles'],
        #    'collectibles': [
        #        hash #comment
        #    ]
        #}
    }
}

platform = {
    1: 'Xbox',
    2: 'Playstation',
    3: 'Steam',
    4: 'Blizzard',
    5: 'Stadia',
    10: 'Demon',
    254: 'BungieNext'
}