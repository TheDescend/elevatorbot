# Queries to create database tables

################################################################
# Persistent Messages

CREATE TABLE persistentMessages (
    messageName TEXT, 
    guildId BIGINT, 
    channelID BIGINT, 
    messageId BIGINT, 
    reactionsIdList BIGINT [], 
    
    PRIMARY KEY(messageName, guildId)
);

################################################################
# Activities

CREATE TABLE PgcrActivities (
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

CREATE TABLE PgcrActivitiesUsersStats (
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

CREATE TABLE PgcrActivitiesUsersStatsWeapons (
	instanceId BIGINT,
	characterId BIGINT,
	membershipId BIGINT,
	
	weaponId BIGINT,
	uniqueWeaponKills INTEGER,
	uniqueWeaponPrecisionKills INTEGER,

	PRIMARY KEY (instanceId, membershipId, characterId, weaponId)
);

CREATE TABLE PgcrActivitiesFailToGet(
	instanceId BIGINT PRIMARY KEY,
	period TIMESTAMP WITHOUT TIME ZONE
);

################################################################
# Destiny Manifest

CREATE TABLE DestinyActivityDefinition(
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

CREATE TABLE DestinyActivityTypeDefinition(
	referenceId BIGINT PRIMARY KEY,
	description TEXT,
	name TEXT
);

CREATE TABLE DestinyActivityModeDefinition(
	referenceId SMALLINT PRIMARY KEY,               
	description TEXT,
	name TEXT,
	hash BIGINT,
	activityModeCategory SMALLINT,
	isTeamBased BOOLEAN,
	friendlyName TEXT
);

CREATE TABLE DestinyCollectibleDefinition(
	referenceId BIGINT PRIMARY KEY,
	description TEXT,
	name TEXT,
	sourceHash BIGINT,
	itemHash BIGINT,
	parentNodeHashes BIGINT []
);

CREATE TABLE DestinyInventoryItemDefinition(
	referenceId BIGINT PRIMARY KEY,
	description TEXT,
	name TEXT,
	bucketTypeHash BIGINT,
	tierTypeHash BIGINT,
	tierTypeName TEXT,
	equippable BOOLEAN
);

CREATE TABLE DestinyRecordDefinition(
	referenceId BIGINT PRIMARY KEY,
	description TEXT,
	name TEXT,
	objectiveHashes BIGINT [],
	ScoreValue INTEGER,
	parentNodeHashes BIGINT []
);
