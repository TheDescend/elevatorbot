import dataclasses

import discord


@dataclasses.dataclass
class DestinyData:
    discord_member: discord.Member
    destiny_id: int
    system: int
