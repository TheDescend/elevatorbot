from __future__ import annotations

from enum import Enum

from bungio.models.base import BaseEnum, EnumMixin


# todo delete
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


# todo delete
class DestinyWeaponTypeEnum(Enum):
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
    LINEAR_FUSION_RIFLE = 22
    GRENADE_LAUNCHER = 23
    SUBMACHINE_GUN = 24
    TRACE_RIFLE = 25
    BOW = 31
    GLAIVE = 33


# todo delete
class DestinyItemSubTypeEnum(Enum):
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
    LINEAR_FUSION_RIFLE = 22
    GRENADE_LAUNCHER = 23
    SUBMACHINE_GUN = 24
    TRACE_RIFLE = 25
    BOW = 31
    GLAIVE = 33

    NONE = 0
    MASK = 19
    SHADER = 20
    ORNAMENT = 21
    HELMET = 26
    GAUNTLETS = 27
    CHEST = 28
    LEG = 29
    CLASS = 30
    REPEATABLE_BOUNTY = 32


# todo delete
class UsableDestinyDamageTypeEnum(Enum):
    NONE = 0
    KINETIC = 1
    ARC = 2
    THERMAL = 3
    VOID = 4
    STASIS = 6


# todo delete
class DestinyDamageTypeEnum(Enum):
    KINETIC = 1
    ARC = 2
    THERMAL = 3
    VOID = 4
    STASIS = 6

    NONE = 0
    RAID = 5


# todo delete
class UsableDestinyAmmunitionTypeEnum(Enum):
    PRIMARY = 1
    SPECIAL = 2
    HEAVY = 3


# todo delete
class DestinyAmmunitionTypeEnum(Enum):
    PRIMARY = 1
    SPECIAL = 2
    HEAVY = 3

    NONE = 0
    UNKNOWN = 4


# todo delete
class DestinyItemTierTypeEnum(Enum):
    UNKNOWN = 0
    CURRENCY = 1
    BASIC = 2
    COMMON = 3
    RARE = 4
    LEGENDARY = 5
    EXOTIC = 6


# keep
class DestinyWeaponSlotEnum(BaseEnum):
    KINETIC = 1498876634
    ENERGY = 2465295065
    POWER = 953998645


# keep
class DestinyPresentationNodeWeaponSlotEnum(BaseEnum):
    KINETIC = 2538646043
    ENERGY = 185103480
    POWER = 3788273704


# keep
class DestinyPresentationNodesEnum(Enum):
    SEALS = 616318467


class UsableDestinyActivityModeTypeEnum(Enum):
    ALL = 0
    RAID = 4
    DUNGEON = 82
    STORY = 2
    STRIKE = 3
    NIGHTFALL = 46
    PATROL = 6
    GAMBIT = 63
    ALL_PVE = 7
    IRON_BANNER = 19
    TRIALS_OF_OSIRIS = 84
    PRIVATE_MATCHES = 32
    ALL_PVP = 5


# todo delete
class DestinyActivityModeTypeEnum(Enum):
    ALL = 0
    RAID = 4
    DUNGEON = 82
    STORY = 2
    STRIKE = 3
    NIGHTFALL = 46
    PATROL = 6
    GAMBIT = 63
    ALL_PVE = 7
    IRON_BANNER = 19
    TRIALS_OF_OSIRIS = 84
    PRIVATE_MATCHES = 32
    ALL_PVP = 5

    RESERVED9 = 9
    CONTROL = 10
    RESERVED11 = 11
    CLASH = 12
    RESERVED13 = 13
    CRIMSON_DOUBLES = 15
    HEROIC_NIGHTFALL = 17
    ALL_STRIKES = 18
    RESERVED20 = 20
    RESERVED21 = 21
    RESERVED22 = 22
    RESERVED24 = 24
    ALL_MAYHEM = 25
    RESERVED26 = 26
    RESERVED27 = 27
    RESERVED28 = 28
    RESERVED29 = 29
    RESERVED30 = 30
    SUPREMACY = 31
    SURVIVAL = 37
    COUNTDOWN = 38
    TRIALS_OF_THE_NINE = 39
    SOCIAL = 40
    TRIALS_COUNTDOWN = 41
    TRIALS_SURVIVAL = 42
    IRON_BANNER_CONTROL = 43
    IRON_BANNER_CLASH = 44
    IRON_BANNER_SUPREMACY = 45
    SCORED_HEROIC_NIGHTFALL = 47
    RUMBLE = 48
    ALL_DOUBLES = 49
    DOUBLES = 50
    PRIVATE_MATCHES_CLASH = 51
    PRIVATE_MATCHES_CONTROL = 52
    PRIVATE_MATCHES_SUPREMACY = 53
    PRIVATE_MATCHES_COUNTDOWN = 54
    PRIVATE_MATCHES_SURVIVAL = 55
    PRIVATE_MATCHES_MAYHEM = 56
    PRIVATE_MATCHES_RUMBLE = 57
    HEROIC_ADVENTURE = 58
    SHOWDOWN = 59
    LOCKDOWN = 60
    SCORCHED = 61
    SCORCHED_TEAM = 62
    ALL_PVE_COMPETITIVE = 64
    BREAKTHROUGH = 65
    FORGE = 66
    SALVAGE = 67
    IRON_BANNER_SALVAGE = 68
    PVP_COMPETITIVE = 69
    PVP_QUICKPLAY = 70
    CLASH_QUICKPLAY = 71
    CLASH_COMPETITIVE = 72
    CONTROL_QUICKPLAY = 73
    CONTROL_COMPETITIVE = 74
    GAMBIT_PRIME = 75
    RECKONING = 76
    MENAGERIE = 77
    VEX_OFFENSIVE = 78
    NIGHTMARE_HUNT = 79
    ELIMINATION = 80
    MOMENTUM = 81
    SUNDIAL = 83


class DestinyInventoryBucketEnum(Enum):
    VAULT = 138197802
    CONSUMABLES = 1469714392
    POSTMASTER = 215593132

    HELMET = 3448274439
    GAUNTLETS = 3551918588
    CHEST = 14239492
    LEG = 20886954
    CLASS = 1585787867

    KINETIC = 1498876634
    ENERGY = 2465295065
    POWER = 953998645

    BRIGHT_DUST = 2689798311
    SHARDS = 2689798309

    @staticmethod
    def all() -> list[DestinyInventoryBucketEnum]:
        return [e for e in DestinyInventoryBucketEnum]
