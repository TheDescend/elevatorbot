import os
import sqlite3
import time
from datetime import datetime, timedelta
import json

DEFAULT_PATH = 'database/userdb.sqlite3'

#### ALL DATABASE RELATED FUNCTIONS ####

#TODO have the DB remember the system of the player

def db_connect(db_path=DEFAULT_PATH):
    """ Returns a connection object for the database """
    con = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES |
                                                sqlite3.PARSE_COLNAMES)
    return con

def insertUser(discordServerID, *, discordID, destinyID):
    """ Inserts a discordID - destinyID mapping into the database, f(discordServerID, discordID = XX, destinyID = YY), returns True if successful """
    con = db_connect()
    product_sql = """INSERT INTO discordGuardiansToken 
        (discordSnowflake, destinyID,signupDate,serverID, token, refresh_token) 
        VALUES (?, ?, ?, ?, ?, ?)"""
    try:
        con.execute(product_sql, (discordID, destinyID, int(time.time()), discordServerID, None, None))
        con.commit()
        con.close()
        return True
    except sqlite3.IntegrityError:
        return False

def getRefreshToken(discordID):
    """ Gets a Users Bungie-Refreshtoken or None """
    con = db_connect()
    c = con.cursor()
    select_sql = """SELECT refresh_token FROM discordGuardiansToken
        WHERE discordSnowflake = ?"""
    c.execute(select_sql, (discordID,))
    results = c.fetchone()
    if len(results) == 1:
        return results[0]
    return None
    

def getToken(discordID):
    """ Gets a Users Bungie-Token or None"""
    con = db_connect()
    c = con.cursor()
    select_sql = """SELECT token FROM discordGuardiansToken
        WHERE discordSnowflake = ?"""
    c.execute(select_sql, (discordID,))
    results = c.fetchone()
    if len(results) == 1:
        return results[0]
    return None

def insertToken(discordID, destinyID, discordServerID, token, refresh_token):
    """ Inserts a User or Token into the database """ #TODO split up in two functions or make a overloaded one?
    
    con = db_connect()
    insert_sql = """INSERT INTO discordGuardiansToken
        (discordSnowflake, destinyID, signupDate, serverID, token, refresh_token) 
        VALUES (?, ?, ?, ?, ?, ?)"""

    update_sql = """
        UPDATE discordGuardiansToken
        SET 
        token = ?,
        refresh_token = ?
        WHERE discordSnowflake = ?"""
    try:
        con.execute(insert_sql, (discordID, destinyID, int(time.time()), discordServerID, token, refresh_token))
        con.commit()
        con.close()
    except sqlite3.IntegrityError:
        con.execute(update_sql, (token, refresh_token, discordID))
        con.commit()
        con.close()

def removeUser(discordID):
    """ Removes a User from the DB (by discordID), returns True if successful"""

    con = db_connect()
    product_sql = """DELETE FROM discordGuardiansToken 
        WHERE discordSnowflake = ? """
    try:
        con.execute(product_sql, (discordID,))
        con.commit()
        con.close()
        return True
    except sqlite3.IntegrityError:
        return False

def lookupDestinyID(discordID):
    """ Takes discordID and returns destinyID """
    con = db_connect()
    getUser = """SELECT destinyID FROM discordGuardiansToken
        WHERE discordSnowflake = ?"""
    result = con.execute(getUser, (discordID,)).fetchone() or [None]
    con.close()
    return result[0]

def lookupDiscordID(destinyID):
    """ Takes destinyID and returns discordID """
    con = db_connect()
    getUser = """SELECT discordSnowflake FROM discordGuardiansToken
        WHERE destinyID = ?"""
    result = con.execute(getUser, (destinyID,)).fetchone() or [None]
    con.close()
    return result[0]

def printall():
    """ **DEBUG** Prints the DB to console """
    con = db_connect()
    getAll = """SELECT * FROM discordGuardiansToken"""
    for row in con.execute(getAll).fetchall():
        print(row)

def getEverything():
    """ **DEBUG** Prints the DB to console """
    con = db_connect()
    cur = con.cursor()
    getAll = "SELECT discordSnowflake, destinyID, serverID, token, refresh_token FROM discordGuardiansToken;"

    resultcur = cur.execute(getAll)
    #print(resultcur)

    result = resultcur.fetchall()
    #print(result)

    return result

def insertIntoMessageDB(messagetext, userid, channelid, msgid, msgdate):
    """ Used to collect messages for markov-chaining, returns True if successful """
    con = db_connect()
    product_sql = """INSERT INTO messagedb 
        (msg, userid, channelid, msgid, msgdate) 
        VALUES (?, ?, ?, ?, DATE(?))"""
    try:
        con.execute(product_sql, (messagetext, userid, channelid, msgid, msgdate))
        con.commit()
        con.close()
        return True
    except sqlite3.IntegrityError:
        return False

def getMarkovPairs():
    """ Gets all the markov-pairs """
    con = db_connect()
    getAll = """SELECT * FROM markovpairs"""
    return con.execute(getAll).fetchall()

    
def insertActivity(instanceID, activityHash, activityDurationSeconds, period, startingPhaseIndex, deaths, playercount, mode):
    """ adds an Activity to the database, not player-specific """
    if instanceID == 4601366967:
        print('insertActivity reached')
    con = db_connect()
    cur = con.cursor()
    sqlite_insert_with_param = """INSERT OR IGNORE INTO 'activities'
                          ('instanceID', 'activityHash', 'activityDurationSeconds', 'period', 'startingPhaseIndex', 'deaths', 'playercount', 'mode') 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    data_tuple = (instanceID, activityHash, activityDurationSeconds, period, startingPhaseIndex, deaths, playercount, mode)
    cur.execute(sqlite_insert_with_param, data_tuple)
    con.commit()

def insertInstanceDetails(instanceID, playerID, characterID, lightlevel, displayname, deaths, opponentsDefeated, completed):
    """ adds player-specific information """
    con = db_connect()
    cur = con.cursor()
    sqlite_insert_with_param = """INSERT OR IGNORE INTO 'instancePlayerPerformance'
                          ('instanceID', 'playerID', 'characterID', 'lightlevel', 'displayname', 'deaths', 'opponentsDefeated', 'completed') 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""

    data_tuple = (instanceID, playerID, characterID, lightlevel, displayname, deaths, opponentsDefeated, completed)
    cur.execute(sqlite_insert_with_param, data_tuple)
    con.commit()

def instanceExists(instanceID):
    con = db_connect()
    cur = con.cursor()
    sqlite_select = f"""SELECT instanceID FROM 'instancePlayerPerformance'
                        WHERE instanceID = ?"""

    data_tuple = (instanceID,)
    cur.execute(sqlite_select, data_tuple)
    return cur.fetchall()

def insertCharacter(playerID, characterID, system):
    """ adds player-specific information """
    con = db_connect()
    cur = con.cursor()
    sqlite_insert_with_param = """INSERT OR IGNORE INTO 'characters'
                          (destinyID, characterID, systemID) 
                          VALUES (?, ?, ?)"""
    data_tuple = (playerID, characterID, system)
    cur.execute(sqlite_insert_with_param, data_tuple)
    con.commit()

def getSystemAndChars(destinyID):
    """ returns pairs of system,character """
    con = db_connect()
    cur = con.cursor()
    sqlite_select = """SELECT systemID, characterID
                    FROM 'characters'
                    WHERE destinyID = ?
                    """
    data_tuple = (destinyID,)
    cur.execute(sqlite_select, data_tuple)
    return list(cur.fetchall())

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
    con = db_connect()
    cur = con.cursor()
    sqlite_select = """
                    SELECT t1.instanceID, t1.period
                    FROM (  SELECT instanceID,period FROM activities
                            WHERE period < ?
                                AND mode = 4) t1
                    JOIN (  SELECT instanceID
                            FROM instancePlayerPerformance
                            WHERE playerID = ?
                            ) ipp 
                    ON (ipp.instanceID = t1.instanceID)
                    ORDER BY period DESC
                    LIMIT 1;
                    """
    data_tuple = (before, destinyID)
    cur.execute(sqlite_select, data_tuple)
    (instanceID,period) = cur.fetchone()
    if not instanceID:
        return None
    sqlite_select = """
                    SELECT lightlevel, displayname, deaths, opponentsDefeated, completed 
                    FROM instancePlayerPerformance
                    WHERE instanceID = ?;
                    """
    data_tuple = (instanceID,)
    cur.execute(sqlite_select, data_tuple)
    result = period.strftime("%d %m %Y") + '\n'
    con.close()
    for row in cur.fetchall():
        (lightlevel, displayname, deaths, opponentsDefeated, completed) = row
        finished = 'finished' if completed else 'left'
        result += f'{displayname} L{lightlevel}: {opponentsDefeated}/{deaths} {finished}\n'
    return result

def getFlawlessList(destinyID):
    """ returns hashes of the flawlessly completed activities """
    con = db_connect()
    cur = con.cursor()
    sqlite_select = """
                    SELECT DISTINCT(t1.activityHash)
                    FROM (  SELECT instanceID, period, activityHash FROM activities
                            WHERE deaths = 0
                            AND startingPhaseIndex = 0) t1
                    JOIN (  SELECT instanceID
                            FROM instancePlayerPerformance
                            WHERE playerID = ?
                            ) ipp
                    ON (ipp.instanceID = t1.instanceID)
                    """
    data_tuple = (destinyID,)
    cur.execute(sqlite_select, data_tuple)
    return [res[0] for res in cur.fetchall()]
    
#######################################################################################
#
#   table discordGuardiansToken     (discordSnowflake, destinyID, signupDate, serverID, token, refresh_token) 
#   table messagedb                 (msg, userid, channelid, msgid, msgdate)
#   table markovpairs               (word1, word2)
#   table characters                (systemID, characterID)
