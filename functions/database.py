import psycopg2
import asyncpg
from datetime import datetime
from sshtunnel import SSHTunnelForwarder

import database.psql_credentials as psql_credentials


""" ALL DATABASE ACCESS FUNCTIONS """
ssh_server = None


async def create_connection_pool():
    global pool
    global ssh_server

    args = {
        "database": psql_credentials.dbname,
        "user": psql_credentials.user,
        "host": psql_credentials.host,
        "password": psql_credentials.password
    }
    if ssh_server:
        args.update({
            "host": "localhost",
            "port": ssh_server.local_bind_port
        })

    try:
        pool = await asyncpg.create_pool(max_size=50, **args)
        print("Connected to DB with asyncpg")

    # create an ssh tunnel to connect to the db from outside the local network and bind that to localhost
    except OSError:
        bind_port = 5432

        ssh_server = SSHTunnelForwarder(
            (psql_credentials.ssh_host, psql_credentials.ssh_port),
            ssh_username=psql_credentials.ssh_user,
            ssh_password=psql_credentials.ssh_password,
            remote_bind_address=("localhost", bind_port))
        ssh_server.start()
        print("Connected via SSH")

        # redo connection
        await create_connection_pool()


async def get_connection_pool():
    return pool


################################################################
# User Management

async def removeUser(discordID):
    """ Removes a User from the DB (by discordID), returns True if successful"""

    delete_sql = """
        DELETE FROM 
            discordGuardiansToken
        WHERE 
            discordSnowflake = $1;"""
    async with pool.acquire() as connection:
        await connection.execute(delete_sql, discordID)

async def updateUser(IDdiscord, IDdestiny, systemID):
    """ Updates a User - DestinyID, SystemID  """

    update_sql = f"""
        UPDATE 
            "discordGuardiansToken"
        SET 
            destinyID = $1,
            systemID = $2
        WHERE 
            discordSnowflake = $3;"""
    async with pool.acquire() as connection:
        await connection.execute(update_sql, IDdestiny, systemID, IDdiscord)


async def lookupDestinyID(discordID):
    """ Takes discordID and returns destinyID """

    select_sql = """
        SELECT 
            destinyID 
        FROM 
            "discordGuardiansToken"
        WHERE 
            discordSnowflake = $1;"""
    async with pool.acquire() as connection:
        return await connection.fetchval(select_sql, discordID)


async def lookupDiscordID(destinyID):
    """ Takes destinyID and returns discordID """

    select_sql = """
        SELECT 
            discordSnowflake 
        FROM 
            "discordGuardiansToken"
        WHERE 
            destinyID = $1;"""
    async with pool.acquire() as connection:
        return await connection.fetchval(select_sql, destinyID)


async def lookupSystem(destinyID):
    """ Takes destinyID and returns system """

    select_sql = """
        SELECT 
            systemID 
        FROM 
            "discordGuardiansToken"
        WHERE 
            destinyID = $1;"""
    async with pool.acquire() as connection:
        return await connection.fetchval(select_sql, destinyID)


async def getAllDestinyIDs():
    """ Returns a list with all discord members destiny ids """

    select_sql = """
        SELECT 
            destinyID 
        FROM 
            "discordGuardiansToken";"""
    async with pool.acquire() as connection:
        result = await connection.fetch(select_sql)
    return [x[0] for x in result]


async def getToken(discordID):
    """ Gets a Users Bungie-Token or None"""

    select_sql = """
        SELECT 
            token 
        FROM 
            "discordGuardiansToken"
        WHERE 
            discordSnowflake = $1;"""
    async with pool.acquire() as connection:
        return await connection.fetchval(select_sql, discordID)


async def getRefreshToken(discordID):
    """ Gets a Users Bungie-Refreshtoken or None """

    select_sql = """
        SELECT 
            refresh_token 
        FROM 
            "discordGuardiansToken"
        WHERE 
            discordSnowflake = $1;"""
    async with pool.acquire() as connection:
        return await connection.fetchval(select_sql, discordID)


async def getTokenExpiry(discordID):
    """ Gets a Users Bungie-Token expiry date and als the refresh token ones or None.
    Retruns list(token_expiry, refresh_token_expiry) or None"""

    select_sql = '''
        SELECT 
            token_expiry, refresh_token_expiry
        FROM 
            "discordGuardiansToken"
        WHERE 
            discordSnowflake = $1;'''

    async with pool.acquire() as connection:
        results = await connection.fetchrow(select_sql, discordID)

    return list(map(datetime.timestamp, results))


async def insertToken(discordID, destinyID, systemID, discordServerID, token, refresh_token, token_expiry, refresh_token_expiry):
    """ Inserts / Updates a User or Token into the database """

    # old users
    if destinyID in await getAllDestinyIDs():
        print('User exists, updating token...')
        await updateUser(discordID, destinyID, systemID)
        await updateToken(destinyID, discordID, token, refresh_token, token_expiry, refresh_token_expiry)

    # new users
    else:
        print('User new, inserting token...')
        insert_sql = """
            INSERT INTO 
                "discordGuardiansToken"
                (discordSnowflake, destinyID, signupDate, serverID, token, refresh_token, systemID, token_expiry, refresh_token_expiry) 
            VALUES 
                ($1, $2, $3, $4, $5, $6, $7, $8, $9);"""

        async with pool.acquire() as connection:
            await connection.execute(insert_sql, discordID, destinyID, datetime.today().date(), discordServerID, token, refresh_token, systemID, datetime.fromtimestamp(token_expiry), datetime.fromtimestamp(refresh_token_expiry))


async def updateToken(destinyID, discordID, token, refresh_token, token_expiry, refresh_token_expiry):
    """ Updates a User - Token, token refresh, token_expiry, refresh_token_expiry  """

    print('Token update initiated')
    update_sql = f"""
        UPDATE 
            "discordGuardiansToken"
        SET 
            token = $1,
            refresh_token = $2,
            token_expiry = $3,
            refresh_token_expiry = $4,
            discordSnowflake = $5
        WHERE 
            destinyID = $6;"""
    async with pool.acquire() as connection:
        await connection.execute(update_sql, token, refresh_token, datetime.fromtimestamp(token_expiry), datetime.fromtimestamp(refresh_token_expiry), discordID, destinyID)


async def setSteamJoinID(IDdiscord, IDSteamJoin):
    """ Updates a User - steamJoinId  """

    update_sql = f"""
        UPDATE 
            "discordGuardiansToken"
        SET 
            steamJoinId = $1
        WHERE 
            discordSnowflake = $2;"""
    async with pool.acquire() as connection:
        await connection.execute(update_sql, IDSteamJoin, IDdiscord)


async def getSteamJoinID(IDdiscord):
    """ Gets a Users steamJoinId or None"""

    select_sql = """
        SELECT 
            steamJoinId 
        FROM 
            "discordGuardiansToken"
        WHERE 
            discordSnowflake = $1;"""
    async with pool.acquire() as connection:
        return await connection.fetchval(select_sql, IDdiscord)


async def getallSteamJoinIDs():
    """ Gets all steamJoinId or []"""

    select_sql = """
        SELECT 
            discordsnowflake, steamJoinId
        FROM 
            "discordGuardiansToken"
        WHERE 
            steamJoinId IS NOT NULL;"""
    async with pool.acquire() as connection:
        return await connection.fetch(select_sql)


async def insertIntoMessageDB(messagetext, userid, channelid, msgid):
    """ Used to collect messages for markov-chaining, returns True if successful """

    insert_sql = """
        INSERT INTO 
            messagedb 
            (msg, userid, channelid, msgid, msgdate) 
        VALUES 
            ($1, $2, $3, $4, $5);"""
    async with pool.acquire() as connection:
        await connection.execute(insert_sql, messagetext, userid, channelid, msgid, datetime.now())


async def getLastActivity(destinyID, mode, before=datetime.now()):
    """ Gets the last activity in the specified mode """

    select_sql = """
        SELECT 
            t1.instanceID, t1.period, t1.directorActivityHash
        FROM (  
            SELECT 
                instanceID, period, directorActivityHash
            FROM 
                PgcrActivities
            WHERE 
                period < $1
                AND $2 = ANY(modes)
        ) AS t1
        JOIN (  
            SELECT 
                instanceID
            FROM 
                PgcrActivitiesUsersStats
            WHERE 
                membershipId = $3
        ) AS ipp 
        ON (
            ipp.instanceID = t1.instanceID
        )
        ORDER BY 
            period DESC
        LIMIT 1;"""
    async with pool.acquire() as connection:
        res = await connection.fetchrow(select_sql, before, int(mode), destinyID)

    # prepare return as a dict
    result = {
        "instanceID": res[0],
        "period": res[1],
        "directorActivityHash": res[2],
    }

    if not res[0]:
        return None
    select_sql = """
        SELECT 
            lightlevel, membershipId, characterClass, deaths, opponentsDefeated, completed, score, timePlayedSeconds, activityDurationSeconds, assists, membershipType
        FROM 
            PgcrActivitiesUsersStats
        WHERE 
        instanceID = $1; """
    async with pool.acquire() as connection:
        instanceInfo = await connection.fetch(select_sql, res[0])

    # prepare return as a dict
    result["activityDurationSeconds"] = instanceInfo[0][8]
    result["score"] = instanceInfo[0][6]
    result["entries"] = []
    for row in instanceInfo:
        data = {
            "membershipID": row[1],
            "membershipType": row[10],
            "characterClass": row[2],
            "lightLevel": row[0],
            "completed": row[5],
            "timePlayedSeconds": row[7],
            "opponentsDefeated": row[4],
            "deaths": row[3],
            "assists": row[9],
        }
        result["entries"].append(data)
    return result


async def getFlawlessList(destinyID):
    """ returns hashes of the flawlessly completed activities """

    select_sql = """
        SELECT DISTINCT
            (t1.activityHash)
        FROM (  
            SELECT 
                instanceID, period, activityHash FROM activities
            WHERE 
                deaths = 0
            AND 
                startingPhaseIndex = 0
        ) AS t1
        JOIN (  
            SELECT 
                instanceID
            FROM 
                instancePlayerPerformance
            WHERE 
                playerID = $1
        ) AS ipp
        ON 
            (ipp.instanceID = t1.instanceID);
        """
    async with pool.acquire() as connection:
        result = await connection.fetch(select_sql, destinyID)
    return [res[0] for res in result]


################################################################
# General
# todo swap most requests to use this. Stops this module from getting really full


async def getEverything(database_table_name: str, select_name: list = None, **where_requirements):
    """
    Gets the complete rows or just the asked for value(s) from the given params. Params are not required
    This is a generator!
    """

    async with pool.acquire() as connection:
        # prepare statement
        select_sql = await connection.prepare(
            f"""
            SELECT 
                {", ".join(select_name) if select_name else "*"}
            FROM 
                {database_table_name}
            {"WHERE" if where_requirements else ""} 
                {", ".join([f"{name}=${i}" for name, i in zip(where_requirements.keys(), range(1, len(where_requirements) + 1))])};"""
        )
        async with connection.transaction():
            async for record in select_sql.cursor(*where_requirements.values()):
                yield record


async def getEverythingRow(database_table_name: str, select_name: list = None, **where_requirements):
    """
    Gets the complete row or just the asked for value(s) from the given params. Params are not required
    Returns only one row
    """

    select_sql = f"""
        SELECT 
            {", ".join(select_name) if select_name else "*"}
        FROM 
            {database_table_name}
        {"WHERE" if where_requirements else ""} 
            {", ".join([f"{name}=${i}" for name, i in zip(where_requirements.keys(), range(1, len(where_requirements) + 1))])};"""

    async with pool.acquire() as connection:
        return await connection.fetchrow(select_sql, *where_requirements.values())


################################################################
# Versioning


async def updateVersion(name: str, version: str):
    """ Updates or inserts the version info for the name, fe. the manifest """

    if not await getVersion(name):
        # insert
        insert_sql = f"""
            INSERT INTO 
                versions
                (name, version)
            VALUES 
                ($1, $2);"""
        async with pool.acquire() as connection:
            await connection.execute(insert_sql, name, version)
        return

    # update
    update_sql = f"""
        UPDATE 
            versions
        SET 
            version = $1
        WHERE 
            name = $2;"""
    async with pool.acquire() as connection:
        await connection.execute(update_sql, version, name)


async def getVersion(name: str):
    """ Gets the version info for the name, fe. the manifest """

    select_sql = f"""
        SELECT 
            version
        FROM 
            versions
        WHERE 
            name = $1;"""
    async with pool.acquire() as connection:
        return await connection.fetchval(select_sql, name)


################################################################
# Persistent Messages


async def insertPersistentMessage(messageName, guildId, channelId, messageId, reactionsIdList):
    """ Inserts a message mapping into the database, returns True if successful False otherwise """

    insert_sql = """
        INSERT INTO 
            persistentMessages
            (messageName, guildId, channelId, messageId, reactionsIdList) 
        VALUES 
            ($1, $2, $3, $4, $5);"""
    async with pool.acquire() as connection:
        await connection.execute(insert_sql, messageName, guildId, channelId, messageId, reactionsIdList)


async def updatePersistentMessage(messageName, guildId, channelId, messageId, reactionsIdList):
    """ Updates a message mapping  """

    update_sql = f"""
        UPDATE 
            persistentMessages
        SET 
            channelId = $1, 
            messageId = $2,
            reactionsIdList = $3
        WHERE 
            messageName = $4 
            AND guildId = $5;"""
    async with pool.acquire() as connection:
        await connection.execute(update_sql, channelId, messageId, reactionsIdList, messageName, guildId)


async def getPersistentMessage(messageName, guildId):
    """ Gets a message mapping given the messageName and guildId and channelId"""

    select_sql = """
        SELECT 
            channelId,
            messageId,
            reactionsIdList
        FROM 
            persistentMessages
        WHERE 
            messageName = $1 
            AND guildId = $2;"""
    async with pool.acquire() as connection:
        return await connection.fetchrow(select_sql, messageName, guildId)


async def deletePersistentMessage(messageName, guildId):
    """ Delete a message given the messageName and guildId"""

    delete_sql = """
        DELETE FROM 
            persistentMessages
        WHERE 
            messageName = $1
            AND guildId = $2;"""
    async with pool.acquire() as connection:
        await connection.execute(delete_sql, messageName, guildId)


async def getAllPersistentMessages():
    """ Gets all messages"""

    select_sql = """
        SELECT 
            *
        FROM 
            persistentMessages;"""
    async with pool.acquire() as connection:
        return await connection.fetch(select_sql)


################################################################
# Destiny Manifest - see database/readme.md for info on table structure


async def deleteEntries(connection, definition_name: str):
    """ Deletes all entries from this definition - clean slate """

    delete_sql = f"""
        DELETE FROM 
            {definition_name};"""
    await connection.execute(delete_sql)


async def updateDestinyDefinition(connection, definition_name: str, referenceId: int, **kwargs):
    """ Insert Rows. Input vars depend on which definition is called"""

    insert_sql = f"""
        INSERT INTO 
            {definition_name}
            (referenceId, {", ".join([str(x) for x in kwargs.keys()])}) 
        VALUES 
            ($1, {', '.join(['$' + str(i+2) for i in range(len(kwargs))])});"""

    await connection.execute(insert_sql, referenceId, *list(kwargs.values()))


async def getDestinyDefinition(definition_name: str, referenceId: int):
    """ gets all the info for the given definition. Return depends on which was called """

    select_sql = f"""
        SELECT 
            * 
        FROM 
            {definition_name}
        WHERE 
            referenceId = $1;"""
    async with pool.acquire() as connection:
        return await connection.fetchrow(select_sql, int(referenceId))


async def getGrandmasterHashes():
    """ Gets all GM nightfall hashes. Makes adding the new ones after a season obsolete """

    select_sql = f"""
        SELECT 
            referenceId
        FROM 
            DestinyActivityDefinition
        WHERE 
            (name LIKE '%Grandmaster%' OR activityLightLevel = 1100)
            AND directActivityModeType = 46;"""
    async with pool.acquire() as connection:
        result = await connection.fetch(select_sql)
    return [x[0] for x in result]


async def getSeals():
    """ Gets all seals. returns ([referenceId, titleName], ...)"""

    not_available = [
        837071607,      # shaxx
        1754815776,     # wishbringer
    ]
    select_sql = f"""
        SELECT 
            referenceId, titleName
        FROM 
            DestinyRecordDefinition
        WHERE 
            hasTitle
            AND referenceId NOT IN ({','.join(['$' + str(i+1) for i in range(len(not_available))])});"""
    async with pool.acquire() as connection:
        return await connection.fetch(select_sql, *not_available)


################################################################
# Activities


async def updateLastUpdated(destinyID, timestamp: datetime):
    """ sets players activities last updated time to the last activity he has done"""

    update_sql = """
        UPDATE 
            "discordGuardiansToken"
        SET 
            activitiesLastUpdated = $1
        WHERE 
            destinyID = $2;"""
    async with pool.acquire() as connection:
        await connection.execute(update_sql, timestamp, destinyID)


async def getLastUpdated(destinyID):
    """ gets last time that players activities were updated as datetime object """

    select_sql = """
        SELECT 
            activitiesLastUpdated 
        FROM 
            "discordGuardiansToken"
        WHERE 
            destinyID = $1;"""
    async with pool.acquire() as connection:
        return await connection.fetchval(select_sql, destinyID)


async def insertPgcrActivities(instanceId, referenceId, directorActivityHash, timePeriod, startingPhaseIndex, mode, modes, isPrivate, membershipType):
    """ Inserts an activity to the DB"""

    if not await getPgcrActivity(instanceId):
        insert_sql = """
            INSERT INTO 
                pgcractivities
                (instanceId, referenceId, directorActivityHash, period, startingPhaseIndex, mode, modes, isPrivate, membershipType) 
            VALUES 
                ($1, $2, $3, $4, $5, $6, $7, $8, $9);"""
        async with pool.acquire() as connection:
            await connection.execute(insert_sql, int(instanceId), referenceId, directorActivityHash, timePeriod, startingPhaseIndex, mode, modes, isPrivate, membershipType)


async def getPgcrActivity(instanceId):
    """ Returns info if instance is already in DB """

    select_sql = """
        SELECT 
            *
        FROM 
            pgcractivities
        WHERE 
            instanceId = $1;"""
    async with pool.acquire() as connection:
        return await connection.fetchrow(select_sql, int(instanceId))


async def getPgcrActivitiesUsersStats(instanceId):
    """ Returns info on PgcrActivitiesUsersStats"""

    select_sql = """
        SELECT 
            *
        FROM 
            PgcrActivitiesUsersStats
        WHERE 
            instanceId = $1;"""
    async with pool.acquire() as connection:
        return await connection.fetch(select_sql, int(instanceId))


async def insertPgcrActivitiesUsersStats(instanceId, membershipId, characterId, characterClass, characterLevel, membershipType, lightLevel, emblemHash, standing, assists, completed, deaths, kills, opponentsDefeated, efficiency, killsDeathsRatio, killsDeathsAssists, score, activityDurationSeconds, completionReason, startSeconds, timePlayedSeconds, playerCount, teamScore, precisionKills, weaponKillsGrenade, weaponKillsMelee, weaponKillsSuper, weaponKillsAbility):
    """ Inserts an activity to the DB"""

    insert_sql = """
        INSERT INTO 
            pgcractivitiesusersstats
            (instanceId, membershipId, characterId, characterClass, characterLevel, 
            membershipType, lightLevel, emblemHash, standing, assists, completed, 
            deaths, kills, opponentsDefeated, efficiency, killsDeathsRatio, killsDeathsAssists, 
            score, activityDurationSeconds, completionReason, startSeconds, timePlayedSeconds, 
            playerCount, teamScore, precisionKills, weaponKillsGrenade, weaponKillsMelee, weaponKillsSuper, weaponKillsAbility) 
        VALUES 
            ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24, $25, $26, $27, $28, $29)
        ON CONFLICT 
            DO NOTHING;"""
    async with pool.acquire() as connection:
        await connection.execute(insert_sql, int(instanceId), int(membershipId), int(characterId), characterClass, int(characterLevel),
            int(membershipType), int(lightLevel), int(emblemHash), int(standing), int(assists), int(completed),
            int(deaths), int(kills), int(opponentsDefeated), float(efficiency), float(killsDeathsRatio), float(killsDeathsAssists),
            int(score), int(activityDurationSeconds), int(completionReason), int(startSeconds), int(timePlayedSeconds),
            int(playerCount), int(teamScore), int(precisionKills), int(weaponKillsGrenade), int(weaponKillsMelee), int(weaponKillsSuper), int(weaponKillsAbility))


async def insertFailToGetPgcrInstanceId(instanceID, period):
    """ insert an instanceID that we failed to get data for """

    insert_sql = """
        INSERT INTO 
            pgcractivitiesfailtoget
            (instanceId, period) 
        VALUES 
            ($1, $2);"""
    async with pool.acquire() as connection:
        await connection.execute(insert_sql, int(instanceID), period)


async def getFailToGetPgcrInstanceId():
    """ get all instanceIDs that we failed to get data for """

    select_sql = """
        SELECT 
            * 
        FROM 
            pgcractivitiesfailtoget;"""
    async with pool.acquire() as connection:
        return await connection.fetch(select_sql)


async def deleteFailToGetPgcrInstanceId(instanceId):
    """ delete instanceID that we failed to get data for """

    delete_sql = """
        DELETE FROM 
            pgcractivitiesfailtoget 
        WHERE 
            instanceId = $1;"""
    async with pool.acquire() as connection:
        await connection.execute(delete_sql, int(instanceId))


async def getClearCount(playerid, activityHashes: list):
    """ Gets the full-clearcount for player <playerid> of activity <activityHash> """

    select_sql = f"""
        SELECT 
            COUNT(t.instanceID)
        FROM (
            SELECT 
                instanceID FROM pgcractivities
            WHERE 
                directorActivityHash IN ({','.join(['$' + str(i+1) for i in range(len(activityHashes))])})
            AND 
                startingPhaseIndex <= 2
        ) t
        JOIN (  
            SELECT
                instanceID
            FROM 
                pgcractivitiesusersstats
            WHERE 
                membershipid = ${len(activityHashes) + 1}  
                AND completed = 1 
                AND completionReason = 0
        ) st 
        ON 
            (t.instanceID = st.instanceID);"""
    async with pool.acquire() as connection:
        return await connection.fetchval(select_sql, *activityHashes, playerid)


async def getInfoOnLowManActivity(raidHashes: list, playercount, membershipid, noCheckpoints=False, score_threshold=None):
    """ Gets the lowman [(instanceId, deaths, kills, timePlayedSeconds, period), ...] for player <membershipid> of activity list(<activityHash>) with a == <playercount>"""

    select_sql = f"""
        SELECT 
            selectedActivites.instanceId, userLowmanCompletions.deaths, userLowmanCompletions.kills, userLowmanCompletions.timePlayedSeconds, selectedActivites.period
        FROM (
            SELECT 
                instanceId, period 
            FROM 
                pgcrActivities
            WHERE 
                directorActivityHash IN ({','.join(['$' + str(i+1) for i in range(len(raidHashes))])})
                {"AND startingPhaseIndex = 0" if noCheckpoints else ""}
        ) AS selectedActivites 
        JOIN (
            SELECT memberCompletedActivities.instanceId, lowManCompletions.playercount, memberCompletedActivities.deaths, memberCompletedActivities.kills, memberCompletedActivities.timePlayedSeconds
                FROM (
                    SELECT
                        instanceId, deaths, kills, timePlayedSeconds
                    FROM 
                        pgcrActivitiesUsersStats
                    WHERE 
                        membershipid = ${len(raidHashes) + 1} 
                        AND kills > 0
                        AND completed = 1
                        AND completionReason = 0
                        {f"AND score > {score_threshold}" if score_threshold else ""}
                ) AS memberCompletedActivities
            JOIN (
                SELECT
                    instanceId, COUNT(DISTINCT membershipId) as playercount
                FROM 
                    pgcrActivitiesUsersStats
                GROUP BY 
                    instanceId
                HAVING
                    COUNT(DISTINCT membershipId) = ${len(raidHashes) + 2}
            ) AS lowManCompletions
            ON 
                memberCompletedActivities.instanceId = lowManCompletions.instanceId
        ) AS userLowmanCompletions
        ON 
            (selectedActivites.instanceID = userLowmanCompletions.instanceID)"""
    async with pool.acquire() as connection:
        return await connection.fetch(select_sql, *raidHashes, membershipid, playercount)


async def getFlawlessHashes(membershipid, activityHashes: list):
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
                        AND membershipid = $1
                ) AS st2
                ON 
                    st1.instanceID = st2.instanceID
                GROUP BY 
                    st1.instanceId, st1.membershipid
            ) AS t2
            ON 
                t1.instanceID = t2.instanceID
            WHERE 
                t1.directorActivityHash IN ({','.join(['$' + str(i+2) for i in range(len(activityHashes))])})
                AND t1.startingPhaseIndex <= 2
            GROUP BY 
                t1.instanceId
        ) AS t
        WHERE
            t.deaths = 0;"""
    async with pool.acquire() as connection:
        return await connection.fetch(select_sql, membershipid, *activityHashes)


async def getForges(destinyID):
    """ Returns # of forges and # of afkforges for destinyID """

    select_sql = """
        SELECT 
            t1.instanceId, t2.kills
        FROM 
            pgcractivities as t1
        JOIN (
            SELECT
                instanceId, membershipid, kills
            FROM 
                pgcrActivitiesUsersStats
        ) as t2
        ON 
            t1.instanceId = t2.instanceId
        WHERE 
            t2.membershipId = $1
            AND t1.mode = 66;"""
    async with pool.acquire() as connection:
        return await connection.fetch(select_sql, destinyID)


async def getActivityHistory(destinyID, mode: int = None, activityHashes: list = None, start_time: datetime = datetime.min, end_time: datetime = datetime.now()):
    """ Returns the activity history for destinyID as a list of tuples """

    select_sql = f"""
        SELECT 
            t1.instanceId
        FROM 
            pgcractivities as t1
        JOIN (
            SELECT
                instanceId, membershipid, completed, completionReason
            FROM 
                pgcrActivitiesUsersStats
        ) as t2
        ON 
            t1.instanceId = t2.instanceId
        WHERE 
            t2.completed = 1
            AND t2.completionReason = 0
            AND t2.membershipId = $1
            AND period >= $2 
            AND period <= $3
            {"AND t1.directorActivityHash IN (" + ",".join([str(x) for x in activityHashes]) + ")" if activityHashes else ""}
            {"AND t1.mode = " + str(mode) if mode else ""};"""
    async with pool.acquire() as connection:
        return await connection.fetch(select_sql, destinyID, start_time, end_time)


################################################################
# Activities Weapon Stats


async def insertPgcrActivitiesUsersStatsWeapons(instanceId, characterId, membershipId, weaponId, uniqueWeaponKills, uniqueWeaponPrecisionKills):
    """ Inserts an activity to the DB"""

    insert_sql = """
        INSERT INTO 
            pgcractivitiesusersstatsweapons
            (instanceId, characterId, membershipId, weaponId, uniqueWeaponKills, uniqueWeaponPrecisionKills) 
        VALUES 
            ($1, $2, $3, $4, $5, $6)
        ON CONFLICT
            DO NOTHING;"""
    async with pool.acquire() as connection:
        await connection.execute(insert_sql, int(instanceId), characterId, membershipId, weaponId, uniqueWeaponKills, uniqueWeaponPrecisionKills)


async def getWeaponInfo(membershipID: int, weaponID: int, characterID: int = None, mode: int = 0, activityID: int = None, start: datetime = datetime.min, end: datetime = datetime.now()):
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
                membershipid = $1
                AND weaponid = $2
                {"AND characterId = " + str(characterID) if characterID else ""}
        ) AS t1
        JOIN(
            SELECT 
                instanceId 
            FROM 
                pgcractivities 
            WHERE 
                period >= $3
                AND period <= $4
                {"AND " + str(mode) + " = ANY(modes)" if mode != 0 else ""}
                {"AND directoractivityhash = " + str(activityID) if activityID else ""}
        ) AS t2 
        ON 
            t1.instanceID = t2.instanceID;"""
    async with pool.acquire() as connection:
        return await connection.fetch(select_sql, membershipID, weaponID, start, end)


async def getTopWeapons(membershipid: int, characterID: int = None, mode: int = 0, activityID: int = None, start: datetime = datetime.min, end: datetime = datetime.now()):
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
                membershipid = $1
                {"AND characterId = " + str(characterID) if characterID else ""}
        ) AS t1
        JOIN(
            SELECT 
                instanceId 
            FROM 
                pgcrActivities 
            WHERE 
                period >= $2
                AND period <= $3
                {"AND " + str(mode) + " = ANY(modes)" if mode != 0 else ""}
                {"AND directoractivityhash = " + str(activityID) if activityID else ""}
        ) AS t2 
        ON 
            t1.instanceID = t2.instanceID
        GROUP BY
            t1.weaponId;"""
    async with pool.acquire() as connection:
        return await connection.fetch(select_sql, membershipid, start, end)
