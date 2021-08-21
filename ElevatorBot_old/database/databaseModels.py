# Queries to insert database tables

database_tables = [
    ################################################################
    # Versioning
    """
    CREATE TABLE  IF NOT EXISTS versions (
        name TEXT PRIMARY KEY,
        version TEXT
    );
    """,
    ################################################################
    # D2 Steam Players
    """
    CREATE TABLE IF NOT EXISTS d2SteamPlayers (
        dateObj TIMESTAMP WITHOUT TIME ZONE PRIMARY KEY, 
        numberOfPlayers INT
    );
    """,
    ################################################################
    # Persistent Messages
    """
    CREATE TABLE IF NOT EXISTS persistentMessages (
        messageName TEXT, 
        guildId BIGINT, 
        channelID BIGINT, 
        messageId BIGINT, 
        reactionsIdList BIGINT [], 
        
        PRIMARY KEY(messageName, guildId)
    );
    """,
    ################################################################
    # Activities
    """
    CREATE TABLE IF NOT EXISTS PgcrActivities (
        instanceId BIGINT PRIMARY KEY, 
        referenceId BIGINT,
        directorActivityHash BIGINT,
        period TIMESTAMP WITHOUT TIME ZONE,
        startingPhaseIndex SMALLINT,
        mode SMALLINT,
        modes SMALLINT [],
        isPrivate BOOLEAN,
        membershipType SMALLINT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS PgcrActivitiesUsersStats (
        instanceId BIGINT,
        membershipId BIGINT,
        characterId BIGINT,
        characterClass TEXT,
        characterLevel SMALLINT,
        membershipType SMALLINT,
        lightLevel INTEGER,
        emblemHash BIGINT,
        standing SMALLINT,
        assists INTEGER,
        completed SMALLINT,
        deaths INTEGER,
        kills INTEGER,
        opponentsDefeated INTEGER,
        efficiency NUMERIC,
        killsDeathsRatio NUMERIC,
        killsDeathsAssists NUMERIC,
        score INTEGER,
        activityDurationSeconds INTEGER,
        completionReason SMALLINT,
        startSeconds INTEGER,
        timePlayedSeconds INTEGER,
        playerCount SMALLINT,
        teamScore INTEGER,
        precisionKills INTEGER,
        weaponKillsGrenade INTEGER,
        weaponKillsMelee INTEGER,
        weaponKillsSuper INTEGER,
        weaponKillsAbility INTEGER,
        
        PRIMARY KEY (instanceId, membershipId, characterId)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS PgcrActivitiesUsersStatsWeapons (
        instanceId BIGINT,
        characterId BIGINT,
        membershipId BIGINT,
        
        weaponId BIGINT,
        uniqueWeaponKills INTEGER,
        uniqueWeaponPrecisionKills INTEGER,
    
        PRIMARY KEY (instanceId, membershipId, characterId, weaponId)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS PgcrActivitiesFailToGet(
        instanceId BIGINT PRIMARY KEY,
        period TIMESTAMP WITHOUT TIME ZONE
    );
    """,
    ################################################################
    # Userdata
    """
    CREATE TABLE IF NOT EXISTS characters(
        destinyID BIGINT,
        characterID BIGINT UNIQUE,
        systemID INTEGER DEFAULT 3,
        UNIQUE(destinyID, characterID)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS discordGuardiansToken(
        discordSnowflake BIGINT PRIMARY KEY,
        destinyID BIGINT,
        signupDate DATE,
        serverID BIGINT,
        token TEXT,
        __refresh_token TEXT,
        systemid INTEGER,
        token_expiry TIMESTAMP,
        refresh_token_expiry TIMESTAMP,
        steamjoinid BIGINT,
        activitiesLastUpdated TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS owned_emblems (
        destiny_id BIGINT, 
        emblem_hash BIGINT
    );
    """,
    ################################################################
    # Destiny Manifest
    """
    CREATE TABLE IF NOT EXISTS DestinyActivityDefinition(
        referenceId BIGINT PRIMARY KEY,
        description TEXT,
        name TEXT,
        activityLevel SMALLINT,
        activityLightLevel INTEGER,
        destinationHash BIGINT,
        placeHash BIGINT,
        activityTypeHash BIGINT,
        isPvP BOOLEAN,
        directActivityModeHash BIGINT,    
        directActivityModeType SMALLINT,  
        activityModeHashes BIGINT [],
        activityModeTypes SMALLINT []
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS DestinyActivityTypeDefinition(
        referenceId BIGINT PRIMARY KEY,
        description TEXT,
        name TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS DestinyActivityModeDefinition(
        referenceId SMALLINT PRIMARY KEY,               
        description TEXT,
        name TEXT,
        hash BIGINT,
        activityModeCategory SMALLINT,
        isTeamBased BOOLEAN,
        friendlyName TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS DestinyCollectibleDefinition(
        referenceId BIGINT PRIMARY KEY,
        description TEXT,
        name TEXT,
        sourceHash BIGINT,
        itemHash BIGINT,
        parentNodeHashes BIGINT []
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS DestinyInventoryItemDefinition(
        referenceId BIGINT PRIMARY KEY,
        description TEXT,
        name TEXT,
        classType SMALLINT,                         -- 0 = titan, 1 = hunter, 2 = warlock
        bucketTypeHash BIGINT,
        tierTypeHash BIGINT,
        tierTypeName TEXT,
        equippable BOOLEAN
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS DestinyRecordDefinition(
        referenceId BIGINT PRIMARY KEY,
        description TEXT,
        name TEXT,
        hasTitle BOOLEAN,                           -- if it is a seal
        titleName TEXT,                             -- this is None for non-seals
        objectiveHashes BIGINT [],
        ScoreValue INTEGER,
        parentNodeHashes BIGINT []
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS DestinyInventoryBucketDefinition(
        referenceId BIGINT PRIMARY KEY,
        description TEXT,
        name TEXT,
        category SMALLINT,
        itemCount SMALLINT,
        location SMALLINT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS DestinyPresentationNodeDefinition(
        referenceId BIGINT PRIMARY KEY,
        description TEXT,
        name TEXT,
        objectiveHash BIGINT,
        presentationNodeType SMALLINT,
        childrenPresentationNodeHash BIGINT [],
        childrenCollectibleHash BIGINT [],
        childrenRecordHash BIGINT [],
        childrenMetricHash BIGINT [],
        parentNodeHashes BIGINT [],
        index SMALLINT,
        redacted BOOLEAN
    );
    """,
    ################################################################
    # LFG System
    """
    CREATE TABLE IF NOT EXISTS LfgUsers(
        user_id BIGINT PRIMARY KEY,
        blacklisted_members BIGINT []
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS LfgMessages(
        id INT PRIMARY KEY,
        guild_id BIGINT,
        channel_id BIGINT,
        message_id BIGINT,
        author_id BIGINT,
        voice_channel_id BIGINT,
        activity TEXT,
        description TEXT,
        start_time TIMESTAMP WITH TIME ZONE,
        creation_time TIMESTAMP WITH TIME ZONE,
        max_joined_members INT,
        joined_members BIGINT [],
        alternate_members BIGINT []
    );
    """,
    ################################################################
    # RSS Feed Reader
    """
    CREATE TABLE IF NOT EXISTS RssFeedItems(
        id TEXT PRIMARY KEY
    );
    """,
    ################################################################
    # Polls
    """
    CREATE TABLE IF NOT EXISTS polls(
        id int PRIMARY KEY,
        name TEXT,
        description TEXT,
        data JSON,
        author_id BIGINT,
        guild_id BIGINT,
        channel_id BIGINT,
        message_id BIGINT
    );
    """,
]
