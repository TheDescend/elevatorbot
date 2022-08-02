from typing import Optional

from Shared.networkingSchemas.base import CustomBaseModel


class DestinyNamedItemModel(CustomBaseModel):
    reference_id: int
    name: str


class DestinyNamedValueItemModel(DestinyNamedItemModel):
    value: float


class DestinyLoreModel(DestinyNamedItemModel):
    description: str
    sub_title: Optional[str] = None
    redacted: bool


class DestinyAllLoreModel(CustomBaseModel):
    items: list[DestinyLoreModel]


class DestinyAllCollectibleModel(CustomBaseModel):
    collectibles: list[DestinyNamedItemModel]


class DestinyAllTriumphModel(CustomBaseModel):
    triumphs: list[DestinyNamedItemModel]


class DestinyAllMaterialsModel(CustomBaseModel):
    basic: list[DestinyNamedValueItemModel] = []
    special: list[DestinyNamedValueItemModel] = []
    transmog: list[DestinyNamedValueItemModel] = []
    crafting: list[DestinyNamedValueItemModel] = []
    upgrading: list[DestinyNamedValueItemModel] = []
