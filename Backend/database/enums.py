from enum import Enum


class DestinyItemTypeEnum(Enum):
    NONE = 0
    CURRENCY = 1
    ARMOR = 2
    WEAPON = 3
    MESSAGE = 7
    ENGRAM = 8
    CONSUMABLE = 9
    EXCHANGE_MATERIAL = 10
    MISSION_REWARD = 11
    QUEST_STEP = 12
    QUEST_STEP_COMPLETE = 13
    EMBLEM = 14
    QUEST = 15
    SUBCLASS = 16
    CLAN_BANNER = 17
    AURA = 18
    MOD = 19
    DUMMY = 20
    SHIP = 21
    VEHICLE = 22
    EMOTE = 23
    GHOST = 24
    PACKAGE = 25
    BOUNTY = 26
    WRAPPER = 27
    SEASONAL_ARTIFACT = 28
    FINISHER = 29


class DestinyItemSubTypeEnum(Enum):
    NONE = 0
    AUTO_RIFLE = 6
    SHOTGUN = 7
    MACHINE_GUN = 8
    HAND_CANNON = 9
    ROCKET_LAUNCHER = 10
    FUSION_RIFLE = 11
    SNIPER_RIFLE = 12
    PULSE_RIFLE = 13
    SCOUT_RIFLE = 14
    SIDEARM = 17
    SWORD = 18
    MASK = 19
    SHADER = 20
    ORNAMENT = 21
    LINEAR_FUSION_RIFLE = 22
    GRENADE_LAUNCHER = 23
    SUB_MACHINE_GUN = 24
    TRACE_RIFLE = 25
    HELMET = 26
    GAUNTLETS = 27
    CHEST = 28
    LEG = 29
    CLASS = 30
    BOW = 31
    REPEATABLE_BOUNTY = 32


class DestinyDamageTypeEnum(Enum):
    NONE = 0
    KINETIC = 1
    ARC = 2
    THERMAL = 3
    VOID = 4
    RAID = 5
    STASIS = 6


class DestinyAmmunitionTypeEnum(Enum):
    NONE = 0
    PRIMARY = 1
    SPECIAL = 2
    HEAVY = 3
    UNKNOWN = 4


class DestinyWeaponSlotEnum(Enum):
    KINETIC = 1498876634
    ENERGY = 2465295065
    POWER = 953998645
