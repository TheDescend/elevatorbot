import psycopg2
from datetime import datetime
from sshtunnel import SSHTunnelForwarder

import database.psql_credentials as psql_credentials

#### ALL DATABASE ACCESS FUNCTIONS ####

con = None
ssh_server = None

def db_connect():
    global con
    """ Returns a connection object for the database """
    if not con:
        print("Connecting to DB")
        try:
            con = psycopg2.connect(
                dbname=psql_credentials.dbname,
                user=psql_credentials.user,
                host=psql_credentials.host,
                password=psql_credentials.password
            )
            con.set_session(autocommit=True)
            print('Opened a DB connection')

        # create an ssh tunnel to connect to the db from outside the local network and bind that to localhost
        except psycopg2.OperationalError:
            bind_port = 5432
            global ssh_server

            ssh_server = SSHTunnelForwarder(
                                    (psql_credentials.ssh_host, psql_credentials.ssh_port),
                                    ssh_username=psql_credentials.ssh_user,
                                    ssh_password=psql_credentials.ssh_password,
                                    remote_bind_address=("localhost", bind_port))
            ssh_server.start()
            print("Connected via SSH")

            con = psycopg2.connect(
                dbname=psql_credentials.dbname,
                user=psql_credentials.user,
                host="localhost",
                port=ssh_server.local_bind_port,
                password=psql_credentials.password
            )
            con.set_session(autocommit=True)
            print('Opened a DB connection via SSH')

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

def setSteamJoinID(IDdiscord, IDSteamJoin):
    """ Updates a User - steamJoinId  """
    update_sql = f"""
        UPDATE 
            "discordGuardiansToken"
        SET 
            steamJoinId = %s
        WHERE 
            discordSnowflake = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(update_sql, (IDSteamJoin, IDdiscord))

def getSteamJoinID(IDdiscord):
    """ Gets a Users steamJoinId or None"""
    select_sql = """
        SELECT 
            steamJoinId 
        FROM 
            "discordGuardiansToken"
        WHERE 
            discordSnowflake = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(select_sql, (IDdiscord,))
        results = cur.fetchone()
        if results:
            return results[0]
    return None

def getallSteamJoinIDs():
    """ Gets all steamJoinId or []"""
    select_sql = """
        SELECT 
            discordsnowflake, steamJoinId
        FROM 
            "discordGuardiansToken"
        WHERE 
            steamJoinId IS NOT NULL;"""
    with db_connect().cursor() as cur:
        cur.execute(select_sql, ())
        results = cur.fetchall()
        return results


def updateUser(IDdiscord, IDdestiny, systemID):
    """ Updates a User - DestinyID, SystemID  """
    update_sql = f"""
        UPDATE 
            "discordGuardiansToken"
        SET 
            destinyID = %s,
            systemID = %s
        WHERE 
            discordSnowflake = %s;"""
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


################################################################
# Persistent Messages


def insertPersistentMessage(messageName, guildId, channelId, messageId, reactionsIdList):
    """ Inserts a message mapping into the database, returns True if successful False otherwise """
    product_sql = """
        INSERT INTO 
            persistentMessages
            (messageName, guildId, channelId, messageId, reactionsIdList) 
        VALUES 
            (%s, %s, %s, %s, %s);"""
    with db_connect().cursor() as cur:
        cur.execute(product_sql, (messageName, guildId, channelId, messageId, reactionsIdList))


def updatePersistentMessage(messageName, guildId, channelId, messageId, reactionsIdList):
    """ Updates a message mapping  """
    update_sql = f"""
        UPDATE 
            persistentMessages
        SET 
            channelId = %s, 
            messageId = %s,
            reactionsIdList = %s
        WHERE 
            messageName = %s AND guildId = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(update_sql, (channelId, messageId, reactionsIdList, messageName, guildId))


def getPersistentMessage(messageName, guildId):
    """ Gets a message mapping given the messageName and guildId"""
    select_sql = """
        SELECT 
            channelId,
            messageId,
            reactionsIdList
        FROM 
            persistentMessages
        WHERE 
            messageName = %s AND guildId = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(select_sql, (messageName, guildId,))
        result = cur.fetchone()
        return result


################################################################
# Destiny Manifest - see database/readme.md for info on table structure


def getDestinyDefinition(definition_name: str, referenceId: int):
    """ gets all the info for the given definition. Return depends on which was called """
    select_sql = f"""
        SELECT 
            * 
        FROM 
            {definition_name}
        WHERE 
            referenceId = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(select_sql, (referenceId,))
        result = cur.fetchone()
        return result


def updateDestinyDefinition(definition_name: str, referenceId: int, **kwargs):
    """ Checks if row exists and inserts/updates accordingly. Input vars depend on which definition is called"""
    result = getDestinyDefinition(definition_name, referenceId)

    # insert
    if not result:
        sql = f"""
            INSERT INTO 
                {definition_name}
                (referenceId, {", ".join([str(x) for x in kwargs.keys()])}) 
            VALUES 
                ({referenceId}, {', '.join(['%s']*len(kwargs))});"""

    # update
    else:
        # check if sth has changed. Start with 1, bc the first entry is the referenceId
        i = 0
        changed = False
        for arg in kwargs.values():
            i += 1
            if arg != result[i]:
                changed = True
                break

        # abort if nothing changed
        if not changed:
            return

        sql = f"""
            UPDATE 
                {definition_name}
            SET 
                {", ".join([str(x) + " = %s" for x in kwargs.keys()])}
            WHERE 
                referenceId = {referenceId};"""
    with db_connect().cursor() as cur:
        params = tuple(kwargs.values())
        cur.execute(sql, params)


################################################################
# Activities


def updateLastUpdated(destinyID, timestamp: datetime):
    """ sets players activities last updated time to the last activity he has done"""
    update_sql = """
        UPDATE 
            "discordGuardiansToken"
        SET 
            activitiesLastUpdated = %s
        WHERE 
            destinyID = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(update_sql, (timestamp, destinyID,))


def getLastUpdated(destinyID):
    """ gets last time that players activities were updated as datetime object """
    select_sql = """
        SELECT 
            activitiesLastUpdated 
        FROM 
            "discordGuardiansToken"
        WHERE 
            destinyID = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(select_sql, (destinyID,))
        results = cur.fetchone()
        if results:
            return results[0]
    return None


def insertPgcrActivities(
    instanceId, referenceId, directorActivityHash, timePeriod, 
    startingPhaseIndex, mode, modes, isPrivate, membershipType):
    """ Inserts an activity to the DB"""
    if not getPgcrActivity(instanceId):
        product_sql = """
            INSERT INTO 
                pgcractivities
                (instanceId, referenceId, directorActivityHash, period, startingPhaseIndex, mode, modes, isPrivate, membershipType) 
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        with db_connect().cursor() as cur:
            cur.execute(product_sql, 
                (instanceId, referenceId, directorActivityHash, timePeriod, 
                startingPhaseIndex, mode, modes, isPrivate, membershipType,))


def getPgcrActivity(instanceId):
    """ Returns info if instance is already in DB"""
    select_sql = """
        SELECT 
            *
        FROM 
            pgcractivities
        WHERE 
            instanceId = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(select_sql, (instanceId,))
        result = cur.fetchone()
        return result


def insertPgcrActivitiesUsersStats(
    instanceId, membershipId, characterId, characterClass, characterLevel, 
    membershipType, lightLevel, emblemHash, standing, assists, completed, 
    deaths, kills, opponentsDefeated, efficiency, killsDeathsRatio, killsDeathsAssists, 
    score, activityDurationSeconds, completionReason, startSeconds, timePlayedSeconds, 
    playerCount, teamScore, precisionKills, weaponKillsGrenade, weaponKillsMelee, weaponKillsSuper, weaponKillsAbility):
    """ Inserts an activity to the DB"""
    product_sql = """
        INSERT INTO 
            pgcractivitiesusersstats
            (instanceId, membershipId, characterId, characterClass, characterLevel, 
            membershipType, lightLevel, emblemHash, standing, assists, completed, 
            deaths, kills, opponentsDefeated, efficiency, killsDeathsRatio, killsDeathsAssists, 
            score, activityDurationSeconds, completionReason, startSeconds, timePlayedSeconds, 
            playerCount, teamScore, precisionKills, weaponKillsGrenade, weaponKillsMelee, weaponKillsSuper, weaponKillsAbility) 
        VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
    with db_connect().cursor() as cur:
        cur.execute(product_sql, 
            (instanceId, membershipId, characterId, characterClass, characterLevel, 
            membershipType, lightLevel, emblemHash, standing, assists, completed, 
            deaths, kills, opponentsDefeated, efficiency, killsDeathsRatio, killsDeathsAssists, 
            score, activityDurationSeconds, completionReason, startSeconds, timePlayedSeconds, 
            playerCount, teamScore, precisionKills, weaponKillsGrenade, weaponKillsMelee, weaponKillsSuper, weaponKillsAbility,))


def insertFailToGetPgcrInstanceId(instanceID, period):
    """ insert an instanceID that we failed to get data for """
    product_sql = """
        INSERT INTO 
            pgcractivitiesfailtoget
            (instanceId, period) 
        VALUES 
            (%s, %s);"""
    with db_connect().cursor() as cur:
        cur.execute(product_sql, (instanceID, period,))


def getFailToGetPgcrInstanceId():
    """ get all instanceIDs that we failed to get data for """
    select_sql = """
        SELECT 
            * 
        FROM 
            pgcractivitiesfailtoget;"""
    with db_connect().cursor() as cur:
        cur.execute(select_sql)
        result = cur.fetchall()
        return result


def deleteFailToGetPgcrInstanceId(instanceId):
    """ delete instanceID that we failed to get data for """
    delete_sql = """
        DELETE FROM 
            pgcractivitiesfailtoget 
        WHERE 
            instanceId = %s;"""
    with db_connect().cursor() as cur:
        cur.execute(delete_sql, (instanceId,))


def getClearCount(playerid, activityHashes: list):
    """ Gets the full-clearcount for player <playerid> of activity <activityHash> """
    select_sql = f"""
        SELECT 
            COUNT(t.instanceID)
        FROM (
            SELECT 
                instanceID FROM pgcractivities
            WHERE 
                directorActivityHash IN ({','.join(['%s']*len(activityHashes))})
            AND 
                startingPhaseIndex <= 2
        ) t
        JOIN (  
            SELECT
                instanceID
            FROM 
                pgcractivitiesusersstats
            WHERE 
                membershipid = %s 
                AND completed = 1 
                AND completionReason = 0
        ) st 
        ON 
            (t.instanceID = st.instanceID);"""
    with db_connect().cursor() as cur:
        cur.execute(select_sql, (*activityHashes, playerid))
        result = cur.fetchone()
        if result:
            return result[0]
    return None


def getInfoOnLowManActivity(raidHashes: list, playercount, membershipid, noCheckpoints=False):
    """ Gets the lowman [(instanceId, deaths, kills, period), ...] for player <membershipid> of activity list(<activityHash>) with a <= <playercount>"""
    select_sql = f"""
        SELECT 
            selectedActivites.instanceId, userLowmanCompletions.deaths, selectedActivites.period
        FROM (
            SELECT 
                instanceId, period 
            FROM 
                pgcrActivities
            WHERE 
                directorActivityHash IN ({','.join(['%s'] * len(raidHashes))})
                {"AND startingPhaseIndex = 0" if noCheckpoints else ""}
        ) AS selectedActivites 
        JOIN (
            SELECT memberCompletedActivities.instanceId, lowManCompletions.playercount, memberCompletedActivities.deaths
                FROM (
                    SELECT
                        instanceId, deaths
                    FROM 
                        pgcrActivitiesUsersStats
                    WHERE 
                        membershipid = %s 
                        AND kills > 0
                        AND completed = 1
                        AND completionReason = 0
                ) AS memberCompletedActivities
            JOIN (
                SELECT
                    instanceId, COUNT(DISTINCT membershipId) as playercount
                FROM 
                    pgcrActivitiesUsersStats
                GROUP BY 
                    instanceId
                HAVING
                    COUNT(DISTINCT membershipId) <= %s
            ) AS lowManCompletions
            ON 
                memberCompletedActivities.instanceId = lowManCompletions.instanceId
        ) AS userLowmanCompletions
        ON 
            (selectedActivites.instanceID = userLowmanCompletions.instanceID)"""
    with db_connect().cursor() as cur:
        cur.execute(select_sql, (*raidHashes, membershipid, playercount))
        result = cur.fetchall()
    return result


def getFlawlessHashes(membershipid, activityHashes: list):
    """ returns the list of all flawless hashes the player has done in the given activityHashes """
    select_sql = f"""
        SELECT 
            t.instanceID
        FROM (
            SELECT 
                t1.instanceID, SUM(t2.deaths) AS deaths
            FROM 
                pgcrActivities AS t1
            JOIN (
                SELECT
                    st1.instanceId, st1.membershipid, SUM(st1.deaths) AS deaths
                FROM 
                    pgcrActivitiesUsersStats as st1
                JOIN (
                    SELECT
                        instanceId
                    FROM 
                        pgcrActivitiesUsersStats
                    WHERE
                        completed = 1
                        AND membershipid = %s
                ) AS st2
                ON 
                    st1.instanceID = st2.instanceID
                GROUP BY 
                    st1.instanceId, st1.membershipid
            ) AS t2
            ON 
                t1.instanceID = t2.instanceID
            WHERE 
                t1.directorActivityHash IN ({','.join(['%s'] * len(activityHashes))})
                AND t1.startingPhaseIndex <= 2
            GROUP BY 
                t1.instanceId
        ) AS t
        WHERE
            t.deaths = 0;"""
    with db_connect().cursor() as cur:
        cur.execute(select_sql, (membershipid, *activityHashes,))
        return cur.fetchall()


################################################################
# Activities Weapon Stats


def insertPgcrActivitiesUsersStatsWeapons(instanceId, characterId, membershipId, weaponId, uniqueWeaponKills, uniqueWeaponPrecisionKills):
    """ Inserts an activity to the DB"""
    product_sql = """
        INSERT INTO 
            pgcractivitiesusersstatsweapons
            (instanceId, characterId, membershipId, weaponId, uniqueWeaponKills, uniqueWeaponPrecisionKills) 
        VALUES 
            (%s, %s, %s, %s, %s, %s);"""
    with db_connect().cursor() as cur:
        cur.execute(product_sql, (instanceId, characterId, membershipId, weaponId, uniqueWeaponKills, uniqueWeaponPrecisionKills,))


def getWeaponInfo(membershipID: int, weaponID: int, characterID: int = None, mode: int = 0, activityID: int = None, start: datetime = datetime.min, end: datetime = datetime.now()):
    """ Gets all the weapon info, for the given parameters.
    Returns (instanceId, uniqueweaponkills, uniqueweaponprecisionkills) """
    select_sql = f"""
        SELECT
            t1.instanceId, t1.uniqueweaponkills, t1.uniqueweaponprecisionkills
        FROM (
            SELECT 
                instanceId, uniqueweaponkills, uniqueweaponprecisionkills
            FROM 
                pgcractivitiesusersstatsweapons
            WHERE 
                membershipid = %s
                AND weaponid = %s
                {"AND characterId = " + str(characterID) if characterID else ""}
        ) AS t1
        JOIN(
            SELECT 
                instanceId 
            FROM 
                pgcractivities 
            WHERE 
                period >= %s
                AND period <= %s
                {"AND " + str(mode) + " = ANY(modes)" if mode != 0 else ""}
                {"AND directoractivityhash = " + str(activityID) if activityID else ""}
        ) AS t2 
        ON 
            t1.instanceID = t2.instanceID;"""
    with db_connect().cursor() as cur:
        cur.execute(select_sql, (membershipID, weaponID, start, end,))
        results = cur.fetchall()
        return results


def getTopWeapons(membershipid: int, characterID: int = None, mode: int = 0, activityID: int = None, start: datetime = datetime.min, end: datetime = datetime.now()):
    """ Gets Top 10 gun for the given parameters.
    Returns (weaponId, uniqueweaponkills, uniqueweaponprecisionkills) """
    select_sql = f"""
        SELECT
            t1.weaponId, SUM(t1.uniqueweaponkills), SUM(t1.uniqueweaponprecisionkills)
        FROM (
            SELECT 
                instanceId, weaponId, uniqueweaponkills, uniqueweaponprecisionkills
            FROM 
                pgcractivitiesusersstatsweapons
            WHERE 
                membershipid = %s
                {"AND characterId = " + str(characterID) if characterID else ""}
        ) AS t1
        JOIN(
            SELECT 
                instanceId 
            FROM 
                pgcrActivities 
            WHERE 
                period >= %s
                AND period <= %s
                {"AND " + str(mode) + " = ANY(modes)" if mode != 0 else ""}
                {"AND directoractivityhash = " + str(activityID) if activityID else ""}
        ) AS t2 
        ON 
            t1.instanceID = t2.instanceID
        GROUP BY
            t1.weaponId;"""
    with db_connect().cursor() as cur:
        cur.execute(select_sql, (membershipid, start, end,))
        results = cur.fetchall()
        return results
