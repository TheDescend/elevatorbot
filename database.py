import os
import sqlite3
import time

# create a default path to connect to and create (if necessary) a database
# called 'database.sqlite3' in the same directory as this script
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'userdb.sqlite3')

def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con

def insertUser(discordServerID, *, discordID, destinyID):
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
    con = db_connect()
    c = con.cursor()
    select_sql = """SELECT refresh_token FROM discordGuardiansToken
        WHERE discordSnowflake = ?"""
    c.execute(select_sql, (discordID,))
    return c.fetchone()[0]
    

def getToken(discordID):
    con = db_connect()
    c = con.cursor()
    select_sql = """SELECT token FROM discordGuardiansToken
        WHERE discordSnowflake = ?"""
    c.execute(select_sql, (discordID,))
    return c.fetchone()[0]

def insertToken(discordID, destinyID, discordServerID, token, refresh_token):
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
    con = db_connect()
    getUser = """SELECT destinyID FROM discordGuardiansToken
        WHERE discordSnowflake = ?"""
    result = con.execute(getUser, (discordID,)).fetchone() or [None]
    con.close()
    return result[0]

def lookupDiscordID(destinyID):
    con = db_connect()
    getUser = """SELECT discordSnowflake FROM discordGuardiansToken
        WHERE destinyID = ?"""
    result = con.execute(getUser, (destinyID,)).fetchone() or [None]
    con.close()
    return result[0]

def printall():
    con = db_connect()
    getAll = """SELECT * FROM discordGuardiansToken"""
    for row in con.execute(getAll).fetchall():
        print(row)

def insertIntoMessageDB(messagetext, userid, channelid, msgid, msgdate):
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
    con = db_connect()
    getAll = """SELECT * FROM markovpairs"""
    return con.execute(getAll).fetchall()

#######################################################################################
#
#   table discordGuardians(discordSnowflake, destinyID,signupDate, serverID)
#   table messagedb(msg, userid, channelid, msgid, msgdate)
#   table markovpairs(word1, word2)
#   
#   
#
#
#
#
#
# general = 670400011519000616
# media = 670400027155365929
# spoilerchat = 670402166103474190
# offtopic = 670362162660900895
#
#
#
#
#
#