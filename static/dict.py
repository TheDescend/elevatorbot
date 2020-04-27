import requests, zipfile, os, pickle, json, sqlite3


getNameFromHashRecords = {}
getNameFromHashActivity= {}
getNameFromHashCollectible = {}
getNameFromHashInventoryItem = {}

# from https://data.destinysets.com/
spirePHashes = [3213556450]
spireHashes = [119944200]
eaterPHashes = [809170886]
eaterHashes = [3089205900]
#there is a hash for each levi-rotation and one for each possible prestige modifier
leviHashes = [2693136600,2693136601,2693136602,2693136603,2693136604,2693136605] 
leviPHashes = [417231112,508802457,757116822, 771164842, 1685065161, 1800508819, 2449714930,3446541099,3857338478,3879860661, 3912437239,4206123728]
scourgeHashes = [548750096] 
lwHashes = [2122313384]
cosHashes = [3333172150, 960175301] 
gosHashes = [3845997235,2659723068]

premenHashes = [2509539864, 2509539865, 2509539867, 1831470693, 3107795800, 3115455134]

zeroHashes = [3232506937] 
herzeroHashes = [2731208666]

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
            'requirements': ['clears'],
            'clears': [
                {'count' : 4,
                'actHashes' : spireHashes + spirePHashes}, #normal
            ],
            'replaced_by': ['Spire of Stars Master']
        },
        'Spire of Stars Master': {
            'requirements': ['clears','flawless'],
            'clears': [
                {'count' : 10,
                'actHashes' : spirePHashes}  #prestige
            ],
            'flawless' : spireHashes + spirePHashes
        },
        'Eater of Worlds': {
            'requirements': ['clears'],
            'clears': [
                {'count' : 4,
                'actHashes' : eaterHashes + eaterPHashes}, #normal
            ],
            'replaced_by':['Eater of Worlds Master']
        },
        'Eater of Worlds Master': {
            'requirements': ['clears','flawless'],
            'clears': [
                {'count' : 10,
                'actHashes' : eaterPHashes}
            ], #prestige
            'flawless': eaterHashes + eaterPHashes
        },
        'Leviathan': {
            'requirements': ['clears'],
            'clears': [
                {'count' : 4,
                'actHashes' : leviHashes + leviPHashes}, #normal
            ],
            'replaced_by': ['Leviathan Master']
        },
        'Leviathan Master': {
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
            ]
        },
        'Y1 Raid Master': {
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
           'replaced_by': ['Crown of Sorrow Master']
       },
        'Crown of Sorrow Master': {
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
            ]
        },
        'Scourge of the Past': {
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
            'replaced_by':['Scourge of the Past Master']
        },
        'Scourge of the Past Master': {
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
            ]
        },
        'Last Wish':{
            'requirements': ['clears','records'],
            'clears' :[
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
            'replaced_by':['Last Wish Master']
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
            ]
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
            'replaced_by':['Garden of Salvation Master']
       },
        'Garden of Salvation Master': {
            'requirements': ['clears','records'],
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
    'Addition':{
        'Niobe\'s Torment': {
            'requirements': ['collectibles'],
            'collectibles': [
                3531075476, #Armory Forged Shell
            ]
        },

        'Solo Flawless Shattered Throne': {
            'requirements': ['records'],
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
            'records': [
                851701008, #Solo Shattered Throne
            ],
            'replaced_by':['Solo Flawless Shattered Throne']
        },

        'The Other Side': {
            'requirements': ['records'],
            'records': [
                807845972, #Only the essentials
            ]
        },

        'Solo Flawless Pit of Heresy': {
            'requirements': ['records'],
            'records': {
                2615277024, #Savior of the Deep
            },
            
        },
        'Solo Pit of Heresy': {
            'requirements': ['records'],
            'records': {
                376114010 , #Usurper
            },
            'replaced_by':['Solo Flawless Pit of Heresy']
        },
        'Flawless Pit of Heresy': {
            'requirements': ['records'],
            'records': {
                3279886460 , #Eternal Heretic
            },
            'replaced_by':['Solo Flawless Pit of Heresy']
        },

        #lowmans

        'Three-Man Argos': {
            'requirements': ['lowman'],
            'playercount' : 3,
            'activityHashes': eaterHashes + eaterPHashes,
            'replaced_by': ['Solo Argos', 'Two-Man Argos'],
         },
        'Two-Man Argos': {
            'requirements': ['lowman'],
            'playercount' : 2,
            'activityHashes': eaterHashes + eaterPHashes,
            'replaced_by': ['Solo Argos'],
         },
        'Solo Argos': {
            'requirements': ['lowman'],
            'playercount' : 1,
            'activityHashes': eaterHashes + eaterPHashes,
         },
        'Three-Man Insurrection': {
            'requirements': ['lowman'],
            'playercount' : 3,
            'activityHashes': scourgeHashes,
            'replaced_by': ['Two-Man Insurrection'],
         },
        'Two-Man Insurrection': {
            'requirements': ['lowman'],
            'playercount' : 2,
            'activityHashes': scourgeHashes,
         },
         'Three-Man Queenswalk': {
            'requirements': ['lowman'],
            'playercount' : 3,
            'activityHashes': lwHashes
         },
         'Two-Man Calus': {
            'requirements': ['lowman'],
            'playercount' : 2,
            'activityHashes': leviHashes + leviPHashes,
         },
         'Three-Man Gahlran': {
            'requirements': ['lowman'],
            'playercount' : 3,
            'activityHashes': cosHashes,
            'replaced_by': ['Two-Man Gahlran'],
         },
         'Two-Man Gahlran': {
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
            'requirements': ['lowman'],
            'playercount' : 3,
            'activityHashes': premenHashes,
            'replaced_by': ['Two-Man Heroic Menagerie', 'Two-Man Heroic Menagerie']
        },
        'Two-Man Heroic Menagerie': {
            'requirements': ['lowman'],
            'playercount' : 2,
            'activityHashes': premenHashes,
            'replaced_by': ['Solo Heroic Menagerie']
        },
        'Solo Heroic Menagerie': {
            'requirements': ['lowman'],
            'playercount' : 1,
            'activityHashes': premenHashes
        },

        'Solo Zero Hour': {
            'requirements': ['lowman'],
            'denyTime0':{ #start is earlier Time, format is important
                'startTime':'10/03/2020 18:00',
                'endTime':'21/04/2020 18:00'
            },
            'playercount' : 1,
            'activityHashes': zeroHashes,
            'replaced_by': ['Solo Flawless Zero Hour']
        },
        'Solo Heroic Zero Hour': {
            'requirements': ['lowman'],
            'denyTime0':{ #start is earlier Time, format is important
                'startTime':'10/03/2020 18:00',
                'endTime':'21/04/2020 18:00'
            },
            'playercount' : 1,
            'activityHashes': herzeroHashes,
            'replaced_by': ['Solo Flawless Heroic Zero Hour']
        },
        'Solo Flawless Zero Hour': {
            'requirements': ['lowman'],
            'playercount' : 1,
            'denyTime0':{ #start is earlier Time, format is important
                'startTime':'10/03/2020 18:00',
                'endTime':'21/04/2020 18:00'
            },
            'flawless' : True,
            'activityHashes': zeroHashes
        },
        'Solo Flawless Heroic Zero Hour': {
            'requirements': ['lowman'],
            'denyTime0':{ #start is earlier Time, format is important
                'startTime':'10/03/2020 18:00',
                'endTime':'21/04/2020 18:00'
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