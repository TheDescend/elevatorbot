import dataclasses

from dis_snek.models import AutocompleteContext
from rapidfuzz import fuzz, process


@dataclasses.dataclass
class DestinyActivityModel:
    name: str
    description: str
    activity_ids: list[int]


@dataclasses.dataclass
class DestinyWeaponModel:
    name: str
    description: str
    flavor_text: str
    weapon_type: str
    weapon_slot: str
    damage_type: str
    ammo_type: str
    reference_ids: list[int]


# all activities are in here at runtime
activities: dict[str, DestinyActivityModel] = {}
activities_by_id: dict[int, DestinyActivityModel] = {}

# all weapons are in here at runtime
weapons: dict[str, DestinyWeaponModel] = {}
weapons_by_id: dict[int, DestinyWeaponModel] = {}


async def autocomplete_send_activity_name(ctx: AutocompleteContext):
    """Send the user the best fitting activities (fuzzy)"""

    best_matches = process.extract(ctx.input_text.lower(), list(activities), scorer=fuzz.WRatio, limit=25)
    await ctx.send(
        choices=[
            {
                "name": activities[match[0]].name,
                "value": activities[match[0]].name,
            }
            for match in best_matches
        ]
    )


async def autocomplete_send_weapon_name(ctx: AutocompleteContext):
    """Send the user the best fitting weapons (fuzzy)"""

    best_matches = process.extract(ctx.input_text.lower(), list(weapons), scorer=fuzz.WRatio, limit=25)
    await ctx.send(
        choices=[
            {
                "name": weapons[match[0]].name,
                "value": weapons[match[0]].name,
            }
            for match in best_matches
        ]
    )
