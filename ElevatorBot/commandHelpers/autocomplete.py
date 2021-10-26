import dataclasses

from dis_snek.models import AutocompleteContext
from rapidfuzz import fuzz, process


@dataclasses.dataclass
class DestinyActivityModel:
    name: str
    description: str
    activity_ids: list[int]


# todo update after manifest update
# all activities are in here at runtime
activities: dict[str, DestinyActivityModel] = {}
activities_by_id: dict[int, DestinyActivityModel] = {}


async def autocomplete_send_activity_name(ctx: AutocompleteContext):
    """Send the user the best fitting activities (fuzzy)"""

    best_matches = process.extract(ctx.input_text.lower(), list(activities), scorer=fuzz.WRatio, limit=25)
    await ctx.send(
        choices=[
            {
                "name": activities[match[0]].name,
                "value": "|".join([str(activity_id) for activity_id in activities[match[0]].activity_ids]),
            }
            for match in best_matches
        ]
    )
