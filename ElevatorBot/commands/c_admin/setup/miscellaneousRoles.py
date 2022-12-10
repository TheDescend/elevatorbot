from typing import Optional

from naff import (
    ActionRow,
    ChannelTypes,
    GuildChannel,
    OptionTypes,
    SelectOption,
    StringSelectMenu,
    slash_command,
    slash_option,
)

from ElevatorBot.commandHelpers.permissionTemplates import restrict_default_permission
from ElevatorBot.commandHelpers.subCommandTemplates import descend_setup_sub_command
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.static.emojis import custom_emojis
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class MiscellaneousRoles(BaseModule):
    _MISC_ROLES: Optional[dict[str, dict]] = None

    def get_misc_roles(self) -> dict[str, dict]:
        """Init or get the other games roles"""

        if not self._MISC_ROLES:
            self._MISC_ROLES = {
                "Among Us": {
                    "emoji": custom_emojis.among_us,
                    "role_id": 750409552075423753,
                },
                "Barotrauma": {
                    "emoji": custom_emojis.barotrauma,
                    "role_id": 738438622553964636,
                },
                "Escape from Tarkov": {
                    "emoji": custom_emojis.eft,
                    "role_id": 800862253279608854,
                },
                "GTA V": {
                    "emoji": custom_emojis.gta,
                    "role_id": 709120893728718910,
                },
                "League of Legends": {
                    "emoji": custom_emojis.lol,
                    "role_id": 756076447881363486,
                },
                "Minecraft": {
                    "emoji": custom_emojis.minecraft,
                    "role_id": 860099222769631242,
                },
                "New World": {
                    "emoji": custom_emojis.new_world,
                    "role_id": 900639721619853322,
                },
                "Varlorant": {
                    "emoji": custom_emojis.valorant,
                    "role_id": 709378171832893572,
                },
                "Formula 1": {
                    "emoji": "🐎",
                    "role_id": 913416199856062485,
                },
            }
        return self._MISC_ROLES

    @slash_command(
        **descend_setup_sub_command,
        sub_cmd_name="miscellaneous_roles",
        sub_cmd_description="Designate a channel in which user can assign themselves miscellaneous roles",
        dm_permission=False,
        scopes=get_setting("COMMAND_GUILD_SCOPE"),
    )
    @slash_option(
        name="channel",
        description="The text channel where the message should be displayed",
        required=True,
        opt_type=OptionTypes.CHANNEL,
        channel_types=[ChannelTypes.GUILD_TEXT],
    )
    @slash_option(
        name="message_id",
        description="You can input a message ID (needs to be from me and selected channel) to have me edit that message",
        required=False,
        opt_type=OptionTypes.STRING,
    )
    @restrict_default_permission()
    async def miscellaneous_roles(self, ctx: ElevatorInteractionContext, channel: GuildChannel, message_id: str = None):
        message_name = "other_game_roles"
        components = [
            ActionRow(
                StringSelectMenu(
                    custom_id=message_name,
                    options=[
                        SelectOption(
                            emoji=game_values["emoji"], label=game_name, value=f"{game_name}|{game_values['role_id']}"
                        )
                        for game_name, game_values in self.get_misc_roles().items()
                    ],
                    placeholder="Select role here",
                    min_values=1,
                    max_values=len(self.get_misc_roles()),
                ),
            ),
        ]
        embed = embed_message("Miscellaneous Roles", "Select options to add / remove the related roles")
        await handle_setup_command(
            ctx=ctx,
            message_name=message_name,
            channel=channel,
            send_message=True,
            send_components=components,
            send_message_embed=embed,
            message_id=int(message_id) if message_id else None,
        )


def setup(client):
    MiscellaneousRoles(client)
