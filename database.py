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
    product_sql = """INSERT INTO discordGuardians 
        (discordSnowflake, destinyID,signupDate,serverID) 
        VALUES (?, ?, ?, ?)"""
    try:
        con.execute(product_sql, (discordID, destinyID, int(time.time()), discordServerID))
        con.commit()
        con.close()
        return True
    except sqlite3.IntegrityError:
        return False

def removeUser(discordID):
    con = db_connect()
    product_sql = """DELETE FROM discordGuardians 
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
    getUser = """SELECT destinyID FROM discordGuardians
        WHERE discordSnowflake = ?"""
    result = con.execute(getUser, (discordID,)).fetchone() or [None]
    con.close()
    return result[0]

def lookupDiscordID(destinyID):
    con = db_connect()
    getUser = """SELECT discordSnowflake FROM discordGuardians
        WHERE destinyID = ?"""
    result = con.execute(getUser, (discordID,)).fetchone() or [None]
    con.close()
    return result[0]

def printall():
    con = db_connect()
    getAll = """SELECT * FROM discordGuardians"""
    for row in con.execute(getAll).fetchall():
        print(row)


#printall()
##table discordGuardians(discordSnowflake, destinyID,signupDate, serverID)