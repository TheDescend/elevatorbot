import os
import sqlite3
import time

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'userdb.sqlite3')

#### ALL DATABASE RELATED FUNCTIONS ####

#TODO have the DB remember the system of the player

def db_connect(db_path=DEFAULT_PATH):
    """ Returns a connection object for the database """
    con = sqlite3.connect(db_path)
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

#######################################################################################
#
#   table discordGuardiansToken     (discordSnowflake, destinyID, signupDate, serverID, token, refresh_token) 
#   table messagedb                 (msg, userid, channelid, msgid, msgdate)
#   table markovpairs               (word1, word2)
#   
