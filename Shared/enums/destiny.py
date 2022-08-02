from __future__ import annotations

from enum import Enum

from bungio.models.base import BaseEnum


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


class DestinyWeaponSlotEnum(BaseEnum):
    KINETIC = 1498876634
    ENERGY = 2465295065
    POWER = 953998645


class DestinyPresentationNodeWeaponSlotEnum(BaseEnum):
    KINETIC = 2538646043
    ENERGY = 185103480
    POWER = 3788273704


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
