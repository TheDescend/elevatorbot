import json
import os
import psycopg2
import time
from datetime import datetime

import database.psql_credentials as psql_credentials

#### ALL DATABASE ACCESS FUNCTIONS ####

con = None
def db_connect():
    global con
    """ Returns a connection object for the database """
    if not con:
        con = psycopg2.connect(
            dbname=psql_credentials.dbname,
            user=psql_credentials.user, 
            host=psql_credentials.host,
            password=psql_credentials.password
        )
        con.set_session(autocommit=True)
        print('opened a db connection')
    return con

def removeUser(discordID):
    """ Removes a User from the DB (by discordID), returns True if successful"""

    product_sql = """DELETE FROM "discordGuardiansToken" 
        WHERE discordSnowflake = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(product_sql, (discordID,))
    return True

    
def insertBountyUser(discordID):
    """ Inserts a discordID mapping into the database, returns True if successful False otherwise """
    product_sql = """INSERT INTO bountyGoblins 
        (discordSnowflake) 
        VALUES (%s);"""
    with db_connect().cursor() as cur:
        cur.execute(product_sql, (discordID,))
    return True

def removeBountyUser(discordID):
    """ Removes a User from the DB (by discordID), returns True if successful. CAREFUL also remove points"""
    product_sql = """DELETE FROM bountyGoblins 
        WHERE discordSnowflake = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(product_sql, (discordID,))
    return True

def getBountyUserList(all=False):
    """ Returns a list of all discordSnowflakes of bountyUsers"""
    extra = "WHERE active = 1"
    if all:
        extra = ""

    getAll = f"""SELECT discordSnowflake FROM bountyGoblins {extra};"""
    with db_connect().cursor() as cur:
        cur.execute(getAll)
        result = cur.fetchall()

    return [row[0] for row in result]


"""
levels: (all INTEGER)
    exp_pve                     # those 3 are for exp levels. 0 for unexp and 1 for exp
    exp_pvp
    exp_raids
    
    points_bounties_pve         # for leaderboards and potential future expansion 
    points_bounties_pvp 
    points_bounties_raids 
    points_competition_pve
    points_competition_pvp
    points_competition_raids
    
    active                      # is the user currently signed up
    notifications DEFAULT 0     # for weekly pings
"""
def getLevel(levelType, discordID):
    """ Returns the level for a specific discordID"""
    getLevelByDiscordID = f"SELECT {levelType} FROM bountyGoblins WHERE discordSnowflake = %s;"
    with db_connect().cursor() as cur:
        cur.execute(getLevelByDiscordID, (discordID,))
        result = cur.fetchall()

    return result[0][0]

def setLevel(value, levelType, discordID):
    """ Adds to a value to a level for a discordID and then returns it"""
    #print(f'{value=} {levelType=} {discordID=}')
    setLevelByDiscordID = f"""   
                    UPDATE bountyGoblins 
                    SET {levelType} = %s 
                    WHERE discordSnowflake = %s;"""
    with db_connect().cursor() as cur:
        resultcur = cur.execute(setLevelByDiscordID, (value, discordID,))
    return True

def addLevel(value, levelType, discordID):
    """ Adds to a value to a level for a discordID and then returns it"""
    curLevel = getLevel(levelType, discordID)
    newLevel = (0 if curLevel is None else curLevel) + (0 if value is None else value)
    setLevelByDiscordID = f"""   
                    UPDATE bountyGoblins 
                    SET {levelType} = %s 
                    WHERE discordSnowflake = %s;"""
    with db_connect().cursor() as cur:
        resultcur = cur.execute(setLevelByDiscordID, (newLevel, discordID,))
    return True


def getRefreshToken(discordID):
    """ Gets a Users Bungie-Refreshtoken or None """
    select_sql = """SELECT refresh_token FROM "discordGuardiansToken"
        WHERE discordSnowflake = %s;"""

    with db_connect().cursor() as cur:
        cur.execute(select_sql, (discordID,))
        results = cur.fetchone()

    if len(results) == 1:
        return results[0]
    return None
    

def getToken(discordID):
    """ Gets a Users Bungie-Token or None"""
    select_sql = """SELECT token FROM "discordGuardiansToken"
        WHERE discordSnowflake = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(select_sql, (discordID,))
        results = cur.fetchone()
        if results:
            return results[0]
    return None


def getTokenExpiry(discordID):
    """ Gets a Users Bungie-Token expiry date and als the refresh token ones or None.
    Retruns tuple (token_expiry, refresh_token_expiry) or None"""
    select_sql = '''SELECT 
        token_expiry, refresh_token_expiry
        FROM 
        "discordGuardiansToken"
        WHERE 
        discordSnowflake = %s;'''
    print(discordID)
    with db_connect().cursor() as cur:
        cur.execute(select_sql, (discordID,))
        results = cur.fetchone()
        #returns datetime objects
    return list(map(datetime.timestamp, results))


def insertToken(discordID, destinyID, systemID, discordServerID, token, refresh_token, token_expiry, refresh_token_expiry):
    """ Inserts a User or Token into the database """ #TODO split up in two functions or make a overloaded one%s
    if destinyID in getAllDestinyIDs():
        print('User exists, updating...')
        updateUser(discordID, destinyID, systemID)
        isTokenUpdated = updateToken(destinyID, discordID,token, refresh_token, token_expiry, refresh_token_expiry)
        assert(isTokenUpdated)
    else:
        print('User new, inserting...')
        insert_sql = """INSERT INTO "discordGuardiansToken"
            (discordSnowflake, destinyID, signupDate, serverID, token, refresh_token, systemID, token_expiry, refresh_token_expiry) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        
        with db_connect().cursor() as cur:
            cur.execute(insert_sql,     (discordID, 
                                        destinyID, 
                                        datetime.today().date(), 
                                        discordServerID, 
                                        token, refresh_token, 
                                        systemID, 
                                        datetime.fromtimestamp(token_expiry), 
                                        datetime.fromtimestamp(refresh_token_expiry)))
        


def updateToken(destinyID, discordID, token, refresh_token, token_expiry, refresh_token_expiry):
    """ Updates a User - Token, token refresh, token_expiry, refresh_token_expiry  """
    print('token update initiated')
    update_sql = f"""
        UPDATE "discordGuardiansToken"
        SET 
        token = %s,
        refresh_token = %s,
        token_expiry = %s,
        refresh_token_expiry = %s,
        discordSnowflake = %s
        WHERE destinyID = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(update_sql, (token, refresh_token, datetime.fromtimestamp(token_expiry), datetime.fromtimestamp(refresh_token_expiry), discordID, destinyID))
        return cur.rowcount > 0

def updateUser(IDdiscord, IDdestiny, systemID):
    """ Updates a User - DestinyID, SystemID  """
    update_sql = f"""
        UPDATE "discordGuardiansToken"
        SET 
        destinyID = %s,
        systemID = %s
        WHERE discordSnowflake = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(update_sql, (IDdestiny, systemID, IDdiscord))



def lookupDestinyID(discordID):
    """ Takes discordID and returns destinyID """

    getUser = """SELECT destinyID FROM "discordGuardiansToken"
        WHERE discordSnowflake = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(getUser, (discordID,))
        if result := cur.fetchone():
            return result[0]
    return None

def lookupDiscordID(destinyID):
    """ Takes destinyID and returns discordID """
    getUser = """SELECT discordSnowflake FROM "discordGuardiansToken"
        WHERE destinyID = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(getUser, (destinyID,))
        if result := cur.fetchone():
            return result[0]
    return None

def lookupServerID(discordID):
    """ Takes destinyID and returns discordID """
    getUser = """SELECT serverID FROM "discordGuardiansToken"
        WHERE discordSnowflake = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(getUser, (discordID,))
        if result := cur.fetchone():
            return result[0]
    return None

def lookupSystem(destinyID):
    """ Takes destinyID and returns system """
    getUser = """SELECT systemID FROM "discordGuardiansToken"
        WHERE destinyID = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(getUser, (destinyID,))
        if result := cur.fetchone():
            return result[0]
    return None

def printall():
    """ **DEBUG** Prints the DB to console """
    getAll = """SELECT * FROM "discordGuardiansToken";"""
    with db_connect().cursor() as cur:
        cur.execute(getAll)
        for row in cur.fetchall():
            print(row)

def getEverything():
    """ **DEBUG** Prints the DB to console """
    getAll = """SELECT discordSnowflake, destinyID, serverID, systemID, token, refresh_token, token_expiry, refresh_token_expiry FROM "discordGuardiansToken";"""
    with db_connect().cursor() as cur:
        cur.execute(getAll)
        result = cur.fetchall()
    return result

def getAllDestinyIDs():
    """ Returns a list with all discord members destiny ids """
    getAll = """SELECT destinyID FROM "discordGuardiansToken";"""
    with db_connect().cursor() as cur:
        cur.execute(getAll)
        result = cur.fetchall()

    return [x[0] for x in result]

def insertIntoMessageDB(messagetext, userid, channelid, msgid):
    """ Used to collect messages for markov-chaining, returns True if successful """
    product_sql = """INSERT INTO messagedb 
        (msg, userid, channelid, msgid, msgdate) 
        VALUES (%s, %s, %s, %s, current_date);"""
    with db_connect().cursor() as cur:
        cur.execute(product_sql, (messagetext, userid, channelid, msgid))
    return True

    
def insertActivity(instanceID, activityHash, activityDurationSeconds, period, startingPhaseIndex, deaths, playercount, mode):
    """ adds an Activity to the database, not player-specific """
    if not activityExists(instanceID):
        sqlite_insert_with_param = """INSERT INTO activities
                            (instanceID, activityHash, activityDurationSeconds, period, startingPhaseIndex, deaths, playercount, mode) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
        data_tuple = (instanceID, activityHash, activityDurationSeconds, period, startingPhaseIndex, deaths, playercount, mode)
        with db_connect().cursor() as cur:
            cur.execute(sqlite_insert_with_param, data_tuple)
        return True
    else:
        return False

def insertInstanceDetails(instanceID, playerID, characterID, lightlevel, displayname, deaths, opponentsDefeated, completed):
    """ adds player-specific information """
    if not playerInstanceExists(instanceID, playerID):
        sqlite_insert_with_param = """INSERT INTO instancePlayerPerformance
                            (instanceID, playerID, characterID, lightlevel, displayname, deaths, opponentsDefeated, completed) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING instanceID;"""
        data_tuple = (instanceID, playerID, characterID, lightlevel, displayname, deaths, opponentsDefeated, completed)
        with db_connect().cursor() as cur:
            cur.execute(sqlite_insert_with_param, data_tuple)
            return cur.fetchone()[0]

def playerInstanceExists(instanceID, playerID = None):
    if playerID:
        sqlite_select = f"""SELECT instanceID FROM instancePlayerPerformance
                            WHERE instanceID = %s AND playerID = %s;"""
        data_tuple = (instanceID, playerID)
    else:
        sqlite_select = f"""SELECT instanceID FROM instancePlayerPerformance
                            WHERE instanceID = %s;"""
        data_tuple = (instanceID, )
    
    with db_connect().cursor() as cur:
        cur.execute(sqlite_select, data_tuple)
        result = cur.fetchall()
    return len(result) > 0

def activityExists(instanceID):
    sqlite_select = f"""SELECT instanceID FROM activities
                        WHERE instanceID = %s;"""
    data_tuple = (instanceID, )
    
    with db_connect().cursor() as cur:
        cur.execute(sqlite_select, data_tuple)
        result = cur.fetchall()
    return len(result) > 0

def getClearCount(playerid, activityHashes):
    """ Gets the full-clearcount for player <playerid> of activity <activityHash> """
    sqlite_select = f"""SELECT COUNT(t1.instanceID)
                        FROM (  SELECT instanceID FROM activities
                                WHERE activityHash IN ({','.join(['%s']*len(activityHashes))})
                                AND startingPhaseIndex <= 2) t1
                        JOIN (  SELECT DISTINCT(instanceID)
                                FROM instancePlayerPerformance
                                WHERE playerID = %s
                                ) ipp 
                        ON (ipp.instanceID = t1.instanceID);
                        """
    data_tuple = (*activityHashes, playerid)
    with db_connect().cursor() as cur:
        cur.execute(sqlite_select, data_tuple)
        (result,) = cur.fetchone()
    return result

def getInfoOnLowManActivity(raidHashes, playercount, playerid):
    #raidHashes = [str(r) for r in raidHashes]
    sqlite_select = f"""SELECT t1.instanceID, t1.deaths, t1.period
                        FROM (  SELECT instanceID, deaths, period FROM activities
                                WHERE activityHash IN ({','.join(['%s']*len(raidHashes))})
                                AND playercount = %s) t1 
                        JOIN (  SELECT DISTINCT(instanceID)
                                FROM instancePlayerPerformance
                                WHERE playerID = %s
                                ) ipp
                        ON (ipp.instanceID = t1.instanceID);
                        """
    data_tuple = (*raidHashes, playercount, playerid)
    with db_connect().cursor() as cur:
        cur.execute(sqlite_select, data_tuple)
        low_activity_info = cur.fetchall()
    return low_activity_info

def hasFlawless(playerid, activityHashes):
    """ returns the list of all flawless raids the player <playerid> has done """
    sqlite_select = f"""SELECT COUNT(t1.instanceID)
                        FROM (  SELECT instanceID FROM activities
                                WHERE activityHash IN ({','.join(['%s']*len(activityHashes))})
                                AND startingPhaseIndex <= 2
                                AND deaths = 0) t1
                        JOIN (  SELECT DISTINCT(instanceID)
                                FROM instancePlayerPerformance
                                WHERE playerID = %s
                                ) ipp 
                        ON (ipp.instanceID = t1.instanceID);
                        """
    data_tuple = (*activityHashes, playerid)
    with db_connect().cursor() as cur:
        cur.execute(sqlite_select, data_tuple)
        (count,) = cur.fetchone()
    return count > 0

def insertCharacter(playerID, characterID, system):
    """ adds player-specific information """
    charlist = getSystemAndChars(playerID)
    if int(characterID) not in [int(syschar[1]) for syschar in charlist]:
        sqlite_insert_with_param = """INSERT INTO characters
                            (destinyID, characterID, systemID) 
                            VALUES (%s, %s, %s);"""
        data_tuple = (playerID, characterID, system)
        with db_connect() as conn, conn.cursor() as cur:
            cur.execute(sqlite_insert_with_param, data_tuple)

def getSystemAndChars(destinyID):
    """ returns pairs of system,character """
    sqlite_select = """SELECT systemID, characterID
                    FROM characters
                    WHERE destinyID = %s;
                    """
    data_tuple = (destinyID,)
    with db_connect().cursor() as cur:
        cur.execute(sqlite_select, data_tuple)
        result = cur.fetchall()
    return result

def updatedPlayer(destinyID):
    """ sets players last updated time to now """
    if not os.path.exists('database/playerUpdated.json'):
        with open('database/playerUpdated.json','w') as f:
            j = dict()
            json.dump(j, f)

    with open('database/playerUpdated.json','r') as f:
        j = json.load(f)
    j[str(destinyID)] = datetime.now().strftime("%d/%m/%Y %H:%M")
    with open('database/playerUpdated.json','w') as f:
        json.dump(j, f)

def getLastUpdated(destinyID):
    """ gets last time that player was updated as datetime object """
    with open('database/playerUpdated.json','r') as f:
        j = json.load(f)
        if str(destinyID) in j.keys():
            datestring = j[str(destinyID)]
            return datetime.strptime(datestring, "%d/%m/%Y %H:%M")
        return datetime.strptime("26/03/1997 21:08", "%d/%m/%Y %H:%M")

def getLastRaid(destinyID, before=datetime.now()):
    sqlite_select = """
                    SELECT t1.instanceID, t1.period
                    FROM (  SELECT instanceID,period FROM activities
                            WHERE period < %s
                                AND mode = 4) t1
                    JOIN (  SELECT instanceID
                            FROM instancePlayerPerformance
                            WHERE playerID = %s
                            ) ipp 
                    ON (ipp.instanceID = t1.instanceID)
                    ORDER BY period DESC
                    LIMIT 1;
                    """
    data_tuple = (before, destinyID)
    with db_connect().cursor() as cur:
        cur.execute(sqlite_select, data_tuple)
        (instanceID, period) = cur.fetchone()
    result = period.strftime("%d %m %Y") + '\n'
    if not instanceID:
        return None
    sqlite_select = """
                    SELECT lightlevel, displayname, deaths, opponentsDefeated, completed 
                    FROM instancePlayerPerformance
                    WHERE instanceID = %s;
                    """
    data_tuple = (instanceID,)
    with db_connect().cursor() as cur:
        cur.execute(sqlite_select, data_tuple)
        instanceInfo = cur.fetchall()
    for row in instanceInfo:
        (lightlevel, displayname, deaths, opponentsDefeated, completed) = row
        finished = 'finished' if completed else 'left'
        result += f'{displayname} L{lightlevel}: {opponentsDefeated}/{deaths} {finished}\n'
    return result

def getFlawlessList(destinyID):
    """ returns hashes of the flawlessly completed activities """
    sqlite_select = """
                    SELECT DISTINCT(t1.activityHash)
                    FROM (  SELECT instanceID, period, activityHash FROM activities
                            WHERE deaths = 0
                            AND startingPhaseIndex = 0) t1
                    JOIN (  SELECT instanceID
                            FROM instancePlayerPerformance
                            WHERE playerID = %s
                            ) ipp
                    ON (ipp.instanceID = t1.instanceID);
                    """
    data_tuple = (destinyID,)
    with db_connect().cursor() as cur:
        cur.execute(sqlite_select, data_tuple)
        result = [res[0] for res in cur.fetchall()]
    return result
