from database.database import getGrandmasterHashes

# from https://data.destinysets.com/
# raids
from functions.event_loop import get_asyncio_loop


spirePHashes = [3213556450]
spireHashes = [119944200]
eaterPHashes = [809170886]
eaterHashes = [3089205900]
# there is a hash for each levi-rotation and one for each possible prestige modifier
leviHashes = [2693136600, 2693136601, 2693136602, 2693136603, 2693136604, 2693136605]
leviPHashes = [417231112, 508802457, 757116822, 771164842, 1685065161, 1800508819, 2449714930, 3446541099, 3857338478,
               3879860661, 3912437239, 4206123728]
scourgeHashes = [548750096]
lwHashes = [2122313384]
cosHashes = [3333172150, 960175301]
gosHashes = [2659723068, 2497200493, 3458480158, 3845997235]
dscHashes = [910380154, 3976949817]
vogHashes = [1485585878, 3711931140, 3881495763]
vogMasterHashes = [1681562271]

# dungeons
throneHashes = [1893059148, 2032534090]
pitHashes = [1375089621, 2559374368, 2559374374, 2559374375]
prophHashes = [1077850348, 4148187374]
harbHashes = [1738383283, ]
presageHashes = [2124066889, ]
presageMasterHashes = [4212753278, ]

# menagerie
premenHashes = [2509539864, 2509539865, 2509539867, 1831470693, 3107795800, 3115455134]

# secret missions
whisperHashes = [74501540]
herwhisperHashes = [1099555105]
zeroHashes = [3232506937]
herzeroHashes = [2731208666]

# nightfalls
loop = get_asyncio_loop()
gmHashes = loop.run_until_complete(getGrandmasterHashes())

# activityTypeHashes
activityStoryHash = [147238405, 1686739444, 1299744814, 2201105581, 2911768360]
activityRaidHash = [2043403989]
activityDungeonHash = [608898761]
activityGambitHash = [636666746, 1418469392, 2490937569]  # will probly change with BL
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

# seasonal challenges hashes
seasonalChallengesCategoryHash = 3443694067

""" Grouped Hashes """
# only activities which are available should be included here
availableRaidHashes = [lwHashes, gosHashes]
raidHashes = availableRaidHashes + [leviHashes, leviPHashes, eaterHashes, eaterPHashes, spireHashes, spirePHashes,
                                    scourgeHashes, cosHashes]
availableDungeonHashes = [throneHashes, pitHashes, prophHashes]

activityStrikeAndNFHash = activityNFHash + activityStrikeHash

metricAvailableRaidCompletion = metricLWCompletions + metricGoSCompletions
metricRaidCompletion = metricAvailableRaidCompletion + metricLeviCompletions + metricEoWCompletions + metricSosCompletions + metricScourgeCompletions + metricCoSCompletions

"""" Speedrun Times: 2x WR for now https://www.speedrun.com/destiny2"""
# has to be tuples bc lists are not hashable
speedrunActivitiesRaids = {
    tuple(scourgeHashes): 648,  # scourge
    tuple(cosHashes): 1118,  # cos
    tuple(lwHashes): 720,  # lw doesn't have a time, so 12mins it is
    tuple(gosHashes): 1496,  # gos
}
# consists of all of them
speedrunActivities = speedrunActivitiesRaids

""" Season and Expansion Dates """
expansion_dates = [
    ["2017-09-06", "D2 Vanilla"],
    ["2018-09-04", "Forsaken"],
    ["2019-10-01", "Shadowkeep"],
    ["2020-11-10", "Beyond Light"],
]
season_dates = [
    ["2017-12-05", "Curse of Osiris"],
    ["2018-05-08", "Warmind"],
    ["2018-12-04", "Season of the Forge"],
    ["2019-03-05", "Season of the Drifter"],
    ["2019-06-04", "Season of Opulence"],
    ["2019-12-10", "Season of Dawn"],
    ["2020-03-10", "Season of the Worthy"],
    ["2020-06-09", "Season of Arrivals"],
    ["2021-02-09", "Season of the Chosen"],
    ["2021-05-11", "Season of the Splicer"],
]

""" Weapon Hashes """
damageTypeKinetic = 3373582085
damageTypeSolar = 1847026933
damageTypeVoid = 3454344768
damageTypeArc = 2303181850

weaponTypeKinetic = 1498876634
weaponTypeEnergy = 2465295065
weaponTypePower = 953998645

possibleWeaponsKinetic = ["Hand Cannon", "Scout Rifle", "Auto Rifle", "Pulse Rifle", "Sidearm", "Submachine Gun",
                          "Combat Bow", "Sniper Rifle", "Shotgun", "Grenade Launcher"]
possibleWeaponsEnergy = ["Hand Cannon", "Scout Rifle", "Auto Rifle", "Pulse Rifle", "Sidearm", "Fusion Rifle",
                         "Shotgun", "Sniper Rifle", "Trace Rifle", "Grenade Launcher", "Combat Bow"]
possibleWeaponsPower = ["Grenade Launcher", "Rocket Launcher", "Linear Fusion Rifle", "Sword", "Shotgun", "Machine Gun",
                        "Sniper Rifle"]

clanids = {
    4107840: 'The Descend'
}

discord_channels = {
    'general': 670400011519000616,
    'media': 670400027155365929,
    'spoilerchat': 670402166103474190,
    'offtopic': 670362162660900895
}

requirementHashes = {
    'Y1': {
        'Spire of Stars': {
            "deprecated": True,
            'requirements': ['clears'],
            'clears': [
                {
                    'count': 4,
                    'actHashes': spireHashes + spirePHashes
                },  # normal
            ],
            'replaced_by': ['Spire of Stars Master', 'Y1 Raid Master']
        },
        'Spire of Stars Master': {
            "deprecated": True,
            'requirements': ['clears', 'flawless'],
            'clears': [
                {
                    'count': 10,
                    'actHashes': spirePHashes
                }  # prestige
            ],
            'flawless': spireHashes + spirePHashes,
            'replaced_by': ['Y1 Raid Master']
        },
        'Eater of Worlds': {
            "deprecated": True,
            'requirements': ['clears'],
            'clears': [
                {
                    'count': 4,
                    'actHashes': eaterHashes + eaterPHashes
                },  # normal
            ],
            'replaced_by': ['Eater of Worlds Master', 'Y1 Raid Master']
        },
        'Eater of Worlds Master': {
            "deprecated": True,
            'requirements': ['clears', 'flawless'],
            'clears': [
                {
                    'count': 10,
                    'actHashes': eaterPHashes
                }
            ],  # prestige
            'flawless': eaterHashes + eaterPHashes,
            'replaced_by': ['Y1 Raid Master']
        },
        'Leviathan': {
            "deprecated": True,
            'requirements': ['clears'],
            'clears': [
                {
                    'count': 4,
                    'actHashes': leviHashes + leviPHashes
                },  # normal
            ],
            'replaced_by': ['Leviathan Master', 'Y1 Raid Master']
        },
        'Leviathan Master': {
            "deprecated": True,
            'requirements': ['clears', 'flawless', 'collectibles'],
            'clears': [
                {
                    'count': 10,
                    'actHashes': leviPHashes
                },  # prestige
            ],
            'flawless': leviHashes + leviPHashes,
            'collectibles': [
                3125541834,  # 1766893932, #good dog
                3125541835,  # 1766893933, #splish splash
                3125541833,  # 1766893935, #two enter, one leaves
                3125541832  # 1766893934  #take the throne
            ],
            'replaced_by': ['Y1 Raid Master']
        },
        'Y1 Raid Master': {
            "deprecated": True,
            'requirements': ['roles'],
            'roles': [
                'Spire of Stars Master',
                'Eater of Worlds Master',
                'Leviathan Master'
            ]
        }
    },
    # TODO anything above here has unchecked hashes
    'Y2': {
        'Crown of Sorrow': {
            "deprecated": True,
            'requirements': ['clears', 'records'],
            'clears': [
                {
                    'count': 15,
                    'actHashes': cosHashes
                }
            ],  # • Minimum 15 full clears
            'records': [
                3308790634,  # Limited Blessings
                3308790637,  # Total Victory
                3308790636,  # With Both Hands
            ],
            'replaced_by': ['Y2 Raid Master', 'Crown of Sorrow Master']
        },
        'Crown of Sorrow Master': {
            "deprecated": True,
            'requirements': ['clears', 'records'],
            'clears': [
                {
                    'count': 30,
                    'actHashes': cosHashes
                }  # Minimum 15 full clears
            ],
            'records': [
                3292013042,  # Crown of Ease [Flawless]
                3292013043,  # Arc Borne :Arc:
                3292013040,  # Void Borne :Void:
                3292013041,  # Solar Borne :Solar:
                3292013054  # Stay Classy [Same Class]
            ],
            'replaced_by': ['Y2 Raid Master']
        },
        'Scourge of the Past': {
            "deprecated": True,
            'requirements': ['clears', 'records'],
            'clears': [
                {
                    'count': 15,
                    'actHashes': scourgeHashes
                }
            ],
            'records': [
                223175561,  # All For One, One For All
                1180238715,  # Hold the Line
                132377266,  # To Each Their Own
                974101911,  # Fast and unwieldy
            ],
            'replaced_by': ['Y2 Raid Master', 'Scourge of the Past Master']
        },
        'Scourge of the Past Master': {
            "deprecated": True,
            'requirements': ['clears', 'records'],
            'clears': [
                {
                    'count': 30,
                    'actHashes': scourgeHashes
                }
            ],
            'records': [
                2925485370,  # Like a Diamond
                # Can't check since not in the api (probably)
                # 772878705,     #Solarstruck
                # 496309570,     #Voidstruck
                # 105811740,     #Thunderstruck
                # 3780682732,    #Stay Classy
            ],
            'replaced_by': ['Y2 Raid Master']
        },
        'Last Wish': {
            'requirements': ['clears', 'records'],
            'clears': [
                {
                    'count': 15,
                    'actHashes': lwHashes
                },  # Minimum 15 full clears
            ],
            'records': [
                1847670729,  # Summoning Ritual
                3533973498,  # Coliseum Champion
                989244596,  # Forever Fight
                3234595894,  # Keep Out
                1711136422  # Strength of Memory
            ],
            'replaced_by': ['Y2 Raid Master', 'Last Wish Master']
        },
        'Last Wish Master': {
            'requirements': ['clears', 'records', 'roles'],
            'roles': [
                'Last Wish'
            ],
            'clears': [
                {
                    'count': 30,
                    'actHashes': lwHashes
                }
            ],  # Minimum 15 full clears
            'records': [
                380332968,  # Petra's Run [Flawless]
                3000516033,  # Thunderstruck :Arc:
                342038729,  # The New Meta [Same Class]
                2826160801,  # Night Owl :Void:
                2588923804,  # Winter's Rest :Stasis:
                623283604  # Sunburn :Solar:
            ],
            'replaced_by': ['Y2 Raid Master']
        },
        'Y2 Raid Master': {
            'requirements': ['roles'],
            'roles': [
                'Last Wish Master',
                'Scourge of the Past Master',
                'Crown of Sorrow Master'
            ]
        }
    },
    'Y3': {
        'Garden of Salvation': {
            'requirements': ['clears', 'records'],
            'clears': [
                {
                    'count': 15,
                    'actHashes': gosHashes
                }  # Minimum 15 full clears
            ],
            'records': [
                3719309782,  # Leftovers
                637935773,  # A Link to the Chain
                2381358572,  # To the Top
                2191554152,  # Zero to One Hundred
            ],
            'replaced_by': ['Garden of Salvation Master', 'Y3 Raid Master']
        },
        'Garden of Salvation Master': {
            'requirements': ['clears', 'records', 'roles'],
            'roles': [
                'Garden of Salvation'
            ],
            'clears': [
                {
                    'count': 30,
                    'actHashes': gosHashes
                }  # Minimum 30 full clears
            ],
            'records': [
                1522774125,  # Inherent Perfection [Flawless]
                3427328428,  # Fluorescent Foliage :Arc:
                277137394,  # Shade in the Garden :Void:
                2571794337,  # Photosynthesis :Solar:
                2629178011,  # Frost on the leaves :Stasis:
                1830799772,  # Garden Party [Same Class]

                4105510833,  # Voltaic Tether
                44547560,  # Repulsion Theory
                3860668859,  # Relay Rally
                3949104239,  # Stop Hitting Yourself
            ],
            'replaced_by': ['Y3 Raid Master']
        },
        'Y3 Raid Master': {
            'requirements': ['roles'],
            'roles': [
                'Garden of Salvation Master'
            ]

        }
    },
    "Y4": {
        'Deep Stone Crypt': {
            'requirements': ['clears', 'records'],
            'clears': [
                {
                    'count': 15,
                    'actHashes': dscHashes
                },  # Minimum 15 full clears
            ],
            'records': [
                22094034,  # Red Rover Challenge
                64856166,  # Copies of Copies Challenge
                337542929,  # Of All Trades Challenge
                2530940166,  # The Core Four Challenge
            ],
            'replaced_by': ['Deep Stone Crypt Master']
        },
        'Deep Stone Crypt Master': {
            'requirements': ['roles', 'clears', 'records'],
            'roles': [
                'Deep Stone Crypt'
            ],
            'clears': [
                {
                    'count': 30,
                    'actHashes': dscHashes
                }
            ],  # Minimum 30 full clears
            'records': [
                3560923614,  # Survival of the Fittest [Flawless]

                134885948,  # Not a Scratch
                4216504853,  # Resource Contention
                3771160417,  # 5 Seconds to Paradise
                1277450448,  # Short Circuit
                1487317889,  # Ready, Set, Go!

                564366615,  # Control Group [Same Class]
                3834307795,  # Electric Sheep :arc:
                3200831458,  # Meltdown :solar:
                513707022,  # Freezing Point :stasis:
                3875695735,  # Devoid of the Rest :void:
            ],
            # 'replaced_by':[]
        },
        'Vault of Glass': {
            'requirements': ['clears', 'records'],
            'clears': [
                {
                    'count': 15,
                    'actHashes': vogHashes + vogMasterHashes
                },  # Minimum 15 full clears
            ],
            'records': [
                # challenges
                706596766,  # wait for it / conflux
                1888851130,  # the only oracle for you / oracles
                154213552,  # out of its way / templar
                2464700601,  # strangers in time / gatekeeper
                1129667036,  # ensemble's refrain / atheon
            ],
            'replaced_by': ['Vault of Glass Master', 'Vault of Glass Grandmaster']
        },
        'Vault of Glass Master': {
            'requirements': ['roles', 'clears', 'records'],
            'roles': [
                'Vault of Glass'
            ],
            'clears': [
                {
                    'count': 30,
                    'actHashes': vogHashes + vogMasterHashes
                }
            ],  # Minimum 30 full clears
            'records': [
                2750088202,  # Flawless Vault of Glass

                1983700615,  # Charged Glass (Arc)
                2592913942,  # Melted Glass (Solar)
                1961032859,  # Empty Glass (Void)
                3969659747,  # Vault of Class (same class)

                874956966,  # Break No Plates (lose no sync plates)
                4170123161,  # Dragon's Den (wyvern only with supers)
                787552349,  # Take Cover (Oracle no goblin kills)
                3903615031,  # Tempered Teleport (Never block teleport)
                3106039192,  # Rabid Relic (only relic super damage for praetorians)
                1024875083,  # Eyes on Atheon (don't kill supplicants)
            ],
            'replaced_by': ['Vault of Glass Grandmaster']
        },
        'Vault of Glass Grandmaster': {
            'requirements': ['roles', 'clears', 'records'],
            'roles': [
                'Vault of Glass',
                'Vault of Glass Master'
            ],
            'clears': [
                {
                    'count': 45,
                    'actHashes': vogHashes + vogMasterHashes
                },
                {
                    'count': 15,
                    'actHashes': vogMasterHashes
                }
            ],
            'records': [
                3790077074,  # Maestro Glasser
            ],
        },
    },
    'Dungeons': {
        'Solo Flawless Shattered Throne': {
            'requirements': ['lowman'],
            'playercount': 1,
            'flawless': True,
            'noCheckpoints': True,
            'denyTime0': {  # start is earlier Time, format is important
                'startTime': '11/08/2020 18:00',
                'endTime': '08/09/2020 18:00'
            },
            'denyTime1': {  # Beyond light boss CP bug
                'startTime': '10/11/2020 18:00',
                'endTime': '17/12/2020 18:00'
            },
            'activityHashes': throneHashes
        },
        'Flawless Shattered Throne': {
            'requirements': ['records'],
            'records': [
                1178448425,  # Curse This
            ],
            'replaced_by': ['Solo Flawless Shattered Throne']
        },
        'Solo Shattered Throne': {
            'requirements': ['records'],
            'denyTime0': {  # start is earlier Time, format is important
                'startTime': '11/08/2020 18:00',  # KEKW
                'endTime': '08/09/2020 18:00'
            },
            'records': [
                3899996566,  # Solo-nely
            ],
            'replaced_by': ['Solo Flawless Shattered Throne']
        },
        'Solo Flawless Pit of Heresy': {
            'requirements': ['lowman'],
            'playercount': 1,
            'flawless': True,
            'noCheckpoints': True,
            'denyTime0': {  # start is earlier Time, format is important
                'startTime': '11/08/2020 18:00',
                'endTime': '08/09/2020 18:00'
            },
            'denyTime1': {  # Beyond light boss CP bug
                'startTime': '10/11/2020 18:00',
                'endTime': '17/12/2020 18:00'
            },
            'activityHashes': pitHashes
        },
        'Solo Pit of Heresy': {
            'requirements': ['records'],
            'denyTime0': {  # start is earlier Time, format is important
                'startTime': '11/08/2020 18:00',
                'endTime': '08/09/2020 18:00'
            },
            'records': {
                3841336511,  # Usurper
            },
            'replaced_by': ['Solo Flawless Pit of Heresy']
        },
        'Flawless Pit of Heresy': {
            'requirements': ['records'],
            'records': {
                245952203,  # Eternal Heretic
            },
            'replaced_by': ['Solo Flawless Pit of Heresy']
        },
        'Solo Prophecy': {
            'requirements': ['records'],
            'records': [
                3002642730
            ],
            'replaced_by': ['Solo Flawless Prophecy']
        },
        'Flawless Prophecy': {
            'requirements': ['records'],
            'records': [
                2010041484
            ],
            'replaced_by': ['Solo Flawless Prophecy']
        },
        'Solo Flawless Prophecy': {
            'requirements': ['lowman', 'records'],
            'records': [
                3191784400  # Solo Flawless Prophecy
            ],
            'playercount': 1,
            'flawless': True,
            'noCheckpoints': True,
            'denyTime0': {  # Beyond light boss CP bug
                'startTime': '10/11/2020 18:00',
                'endTime': '08/09/2020 18:00'
            },
            'denyTime1': {  # start is earlier Time, format is important
                'startTime': '01/12/2020 18:00',
                'endTime': '17/12/2020 18:00'
            },
            'activityHashes': prophHashes
        },
        'Solo Harbinger': {
            'requirements': ['records'],
            'records': [
                3657275647  # Lone Harbinger
            ],
            'replaced_by': ['Solo Flawless Harbinger']
        },
        'Flawless Harbinger': {
            'requirements': ['records'],
            'records': [
                2902814383  # Immortal Harbinger
            ],
            'replaced_by': ['Solo Flawless Harbinger']
        },
        'Solo Flawless Harbinger': {
            'requirements': ['records'],
            'records': [
                3047181179  # Alpha Hunter
            ]
        },
        'Solo Presage': {
            'requirements': ['lowman'],
            'playercount': 1,
            'flawless': False,
            'activityHashes': presageHashes,
            'replaced_by': ['Solo Flawless Presage', 'Solo Master Presage', 'Solo Flawless Master Presage']
        },
        'Flawless Presage': {
            'requirements': ['flawless'],
            'flawless': presageHashes,
            'replaced_by': ['Solo Flawless Presage', 'Flawless Master Presage', 'Solo Flawless Master Presage']
        },
        'Solo Flawless Presage': {
            'requirements': ['records'],
            'records': [
                4206923617  # Lone Gun in a Dark Place 
            ],
            'replaced_by': ['Solo Flawless Master Presage']
        },
        'Solo Master Presage': {
            'requirements': ['lowman'],
            'playercount': 1,
            'flawless': False,
            'activityHashes': presageMasterHashes,
            'replaced_by': ['Solo Flawless Master Presage']
        },
        'Flawless Master Presage': {
            'requirements': ['records'],
            'records': [
                2335417976  # Tale Told
            ],
            'replaced_by': ['Solo Flawless Master Presage']
        },
        'Solo Flawless Master Presage': {
            'requirements': ['lowman'],
            'playercount': 1,
            'flawless': True,
            'activityHashes': presageMasterHashes,
        }
    },
    "Lowmans": {
        'Trio Argos': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount': 3,
            'activityHashes': eaterHashes + eaterPHashes,
            'replaced_by': ['Solo Argos', 'Duo Argos'],
        },
        'Duo Argos': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount': 2,
            'activityHashes': eaterHashes + eaterPHashes,
            'replaced_by': ['Solo Argos'],
        },
        'Solo Argos': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount': 1,
            'activityHashes': eaterHashes + eaterPHashes,
        },
        'Trio Insurrection': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount': 3,
            'activityHashes': scourgeHashes,
            'replaced_by': ['Duo Insurrection'],
        },
        'Duo Insurrection': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount': 2,
            'activityHashes': scourgeHashes,
        },
        'Solo Queenswalk': {
            'requirements': ['lowman'],
            'playercount': 1,
            'activityHashes': lwHashes
        },
        'Duo Queenswalk': {
            'requirements': ['lowman'],
            'playercount': 2,
            'activityHashes': lwHashes,
            'replaced_by': ['Solo Queenswalk']
        },
        'Trio Queenswalk': {
            'requirements': ['lowman'],
            'playercount': 3,
            'activityHashes': lwHashes,
            'replaced_by': ['Solo Queenswalk', 'Duo Queenswalk']
        },
        'Duo Calus': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount': 2,
            'activityHashes': leviHashes + leviPHashes,
        },
        'Trio Gahlran': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount': 3,
            'activityHashes': cosHashes,
            'replaced_by': ['Duo Gahlran'],
        },
        'Duo Gahlran': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount': 2,
            'activityHashes': cosHashes,
        },
        'Duo Sanctified Mind': {
            'requirements': ['lowman'],
            'playercount': 2,
            'activityHashes': gosHashes,
        },
        'Trio Sanctified Mind': {
            'requirements': ['lowman'],
            'playercount': 3,
            'activityHashes': gosHashes,
            'replaced_by': ['Duo Sanctified Mind'],
        },
        'Trio Heroic Menagerie': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount': 3,
            'activityHashes': premenHashes,
            'replaced_by': ['Duo Heroic Menagerie', 'Solo Heroic Menagerie']
        },
        'Duo Heroic Menagerie': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount': 2,
            'activityHashes': premenHashes,
            'replaced_by': ['Solo Heroic Menagerie']
        },
        'Solo Heroic Menagerie': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount': 1,
            'activityHashes': premenHashes
        },
        'Trio Taniks': {
            'requirements': ['lowman'],
            'playercount': 3,
            'activityHashes': dscHashes,
            'replaced_by': ['Duo Taniks']
        },
        'Duo Taniks': {
            'requirements': ['lowman'],
            'playercount': 2,
            'activityHashes': dscHashes
        },
        'Trio Atheon': {
            'requirements': ['lowman'],
            'playercount': 3,
            'activityHashes': vogHashes + vogMasterHashes,
            'replaced_by': ['Duo Atheon']
        },
        'Duo Atheon': {
            'requirements': ['lowman'],
            'playercount': 2,
            'activityHashes': vogHashes + vogMasterHashes
        },
    },
    'Addition': {
        'Niobe\'s Torment': {
            "deprecated": True,
            'requirements': ['collectibles'],
            'collectibles': [
                3531075476,  # Armory Forged Shell
            ]
        },
        'The Other Side': {
            "deprecated": True,
            'requirements': ['records'],
            'denyTime0': {  # start is earlier Time, format is important
                'startTime': '11/08/2020 18:00',
                'endTime': '08/09/2020 18:00'
            },
            'records': [
                1662610173,  # Only the essentials
            ]
        },
        'Solo Zero Hour': {
            "deprecated": True,
            'requirements': ['lowman'],
            'denyTime0': {  # start is earlier Time, format is important
                'startTime': '10/03/2020 18:00',
                'endTime': '21/04/2020 18:00'
            },
            'denyTime1': {  # start is earlier Time, format is important
                'startTime': '11/08/2020 18:00',
                'endTime': '08/09/2020 18:00'
            },
            'playercount': 1,
            'activityHashes': zeroHashes,
            'replaced_by': ['Solo Flawless Zero Hour']
        },
        'Solo Heroic Zero Hour': {
            "deprecated": True,
            'requirements': ['lowman'],
            'denyTime0': {  # start is earlier Time, format is important
                'startTime': '10/03/2020 18:00',
                'endTime': '21/04/2020 18:00'
            },
            'denyTime1': {  # start is earlier Time, format is important
                'startTime': '11/08/2020 18:00',
                'endTime': '08/09/2020 18:00'
            },
            'playercount': 1,
            'activityHashes': herzeroHashes,
            'replaced_by': ['Solo Flawless Heroic Zero Hour']
        },
        'Solo Flawless Zero Hour': {
            "deprecated": True,
            'requirements': ['lowman'],
            'playercount': 1,
            'denyTime0': {  # start is earlier Time, format is important
                'startTime': '10/03/2020 18:00',
                'endTime': '21/04/2020 18:00'
            },
            'denyTime1': {  # start is earlier Time, format is important
                'startTime': '11/08/2020 18:00',
                'endTime': '08/09/2020 18:00'
            },
            'flawless': True,
            'activityHashes': zeroHashes
        },
        'Solo Flawless Heroic Zero Hour': {
            "deprecated": True,
            'requirements': ['lowman'],
            'denyTime0': {  # start is earlier Time, format is important
                'startTime': '10/03/2020 18:00',
                'endTime': '21/04/2020 18:00'
            },
            'denyTime1': {  # start is earlier Time, format is important
                'startTime': '11/08/2020 18:00',
                'endTime': '08/09/2020 18:00'
            },
            'playercount': 1,
            'flawless': True,
            'activityHashes': herzeroHashes
        },
        'Flawless GM': {
            'requirements': ['flawless'],
            'flawless': gmHashes,
            'replaced_by': ['Solo Flawless GM', "Solo Flawless 150k GM"]
        },
        'Solo Flawless GM': {
            'requirements': ['lowman'],
            'playercount': 1,
            'flawless': True,
            'activityHashes': gmHashes,
            'replaced_by': ['Solo Flawless 150k GM']
        },
        'Solo Flawless 150k GM': {
            'requirements': ['lowman'],
            'playercount': 1,
            'flawless': True,
            'score': 150_000,
            'activityHashes': gmHashes,
        },
    }
}
requirement_hashes_without_years = {
    rolename: roledata
    for year, yeardata in requirementHashes.items()
    for rolename, roledata in yeardata.items()
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
