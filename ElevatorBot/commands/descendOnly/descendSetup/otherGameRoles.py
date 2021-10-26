from dis_snek.models import (
    ActionRow,
    GuildChannel,
    GuildText,
    InteractionContext,
    OptionTypes,
    Select,
    SelectOption,
    slash_command,
    slash_option,
)

from ElevatorBot.commandHelpers.responseTemplates import respond_wrong_channel_type
from ElevatorBot.commandHelpers.subCommandTemplates import (
    descend_setup_sub_command,
    setup_sub_command,
)
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import handle_setup_command
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.emojis import custom_emojis
from settings import COMMAND_GUILD_SCOPE


class OtherGameRoles(BaseScale):
    other_games: dict = {
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
    }

    # todo perms
    @slash_command(
        **descend_setup_sub_command,
        sub_cmd_name="other_game_roles",
        sub_cmd_description="Setup a channel in which user can assign themselves other game roles",
        scopes=COMMAND_GUILD_SCOPE,
    )
    @slash_option(
        name="channel",
        description="The text channel where the message should be displayed",
        required=True,
        opt_type=OptionTypes.CHANNEL,
    )
    @slash_option(
        name="message_id",
        description="You can input a message ID to have me edit that message instead of sending a new one. Message must be from me and in the input channel",
        required=False,
        opt_type=OptionTypes.INTEGER,
    )
    async def _other_game_roles(self, ctx: InteractionContext, channel: GuildChannel, message_id: int = None):
        # make sure the channel is a text channel
        if not isinstance(channel, GuildText):
            await respond_wrong_channel_type(ctx=ctx)
            return

        message_name = "other_game_roles"
        components = [
            ActionRow(
                Select(
                    # todo callback
                    custom_id=message_name,
                    options=[
                        SelectOption(
                            emoji=game_values["emoji"], label=game_name, value=f"{game_name}|{game_values['role_id']}"
                        )
                        for game_name, game_values in self.other_games.items()
                    ],
                    placeholder="Select role here",
                    min_values=1,
                    max_values=len(self.other_games),
                ),
            ),
        ]
        embed = embed_message("Other Game Roles", "Select options to add / remove the related roles")
        await handle_setup_command(
            ctx=ctx,
            message_name=message_name,
            channel=channel,
            send_message=True,
            send_components=components,
            send_message_embed=embed,
            message_id=message_id,
        )


def setup(client):
    OtherGameRoles(client)
