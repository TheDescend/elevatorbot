from Backend.crud.base import CRUDBase
from Backend.database.models import (
    DestinyActivityDefinition,
    DestinyActivityModeDefinition,
    DestinyActivityTypeDefinition,
    DestinyCollectibleDefinition,
    DestinyInventoryBucketDefinition,
    DestinyInventoryItemDefinition,
    DestinyPresentationNodeDefinition,
    DestinyRecordDefinition,
    ManifestVersion,
)


class CRUDManifestVersions(CRUDBase):
    pass


class CRUDManifest(CRUDBase):
    pass


manifest_version = CRUDManifestVersions(ManifestVersion)
destiny_activity_definition = CRUDManifest(DestinyActivityDefinition)
destiny_activity_mode_definition = CRUDManifest(DestinyActivityModeDefinition)
destiny_activity_type_definition = CRUDManifest(DestinyActivityTypeDefinition)
destiny_collectible_definition = CRUDManifest(DestinyCollectibleDefinition)
destiny_inventory_bucket_definition = CRUDManifest(DestinyInventoryBucketDefinition)
destiny_inventory_item_definition = CRUDManifest(DestinyInventoryItemDefinition)
destiny_presentation_node_definition = CRUDManifest(DestinyPresentationNodeDefinition)
destiny_record_definition = CRUDManifest(DestinyRecordDefinition)
