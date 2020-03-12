# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
import sqlite3
con = sqlite3.connect('userdb.sqlite3')
cur = con.cursor()


# cur.execute('''
#     DROP TABLE characters
#''')

cur.execute('''
    CREATE TABLE characters(
        destinyID INTEGER UNIQUE,
        characterID INTEGER UNIQUE,
        systemID INTEGER DEFAULT 3,
        UNIQUE(destinyID, characterID)
    )
''')

# cur.execute('''
#     DROP TABLE activities
# ''')

cur.execute('''
    CREATE TABLE activities(
        instanceID INTEGER PRIMARY KEY,
        activityHash INTEGER,
        timePlayedSeconds INTEGER,
        period TIMESTAMP,
        startingPhaseIndex INTEGER,
        completed INTEGER,
        deaths INTEGER,
        playercount INTEGER,
        mode INTEGER
    );
''')

# cur.execute('''
#     DROP TABLE instancePlayerPerformance
#''')

cur.execute('''
    CREATE TABLE instancePlayerPerformance(
        instanceID INTEGER,
        playerID INTEGER,
        characterID INTEGER,
        lightlevel INTEGER,
        displayname TEXT,
        deaths INTEGER,
        opponentsDefeated INTEGER,
        completed INTEGER,
        UNIQUE(instanceID, characterID)
    )
''')

#   discordGuardiansToken     (discordSnowflake, destinyID, signupDate, serverID, token, refresh_token) 
#   table messagedb                 (msg, userid, channelid, msgid, msgdate)
#   table markovpairs               (word1, word2)


# %%
con.commit()
con.close()


# %%


