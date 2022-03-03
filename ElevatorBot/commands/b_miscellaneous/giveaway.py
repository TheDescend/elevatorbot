from dis_snek import (
    ActionRow,
    Button,
    ButtonStyles,
    InteractionContext,
    Member,
    OptionTypes,
    slash_command,
    slash_option,
)

from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.misc.giveaway import BackendGiveaway
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class Giveaway(BaseScale):
    # todo perm
    @slash_command(name="giveaway", description="Creates a giveaway", scopes=get_setting("COMMAND_GUILD_SCOPE"))
    @slash_option(
        name="description", description="Input details about the giveaway", opt_type=OptionTypes.STRING, required=True
    )
    @slash_option(
        name="host",
        description="The user which is hosting the giveaway if it is not you",
        opt_type=OptionTypes.USER,
        required=False,
    )
    async def giveaway(self, ctx: InteractionContext, description: str, host: Member = None):
        if ctx.author.id != 238388130581839872:
            await ctx.send(
                "This is blocked for now, since it it waiting for a vital unreleased discord feature", ephemeral=True
            )
            return

        member = host or ctx.author

        # firstly create the giveaway in the db
        components = [
            ActionRow(
                Button(
                    label="Join",
                    custom_id="giveaway",
                    style=ButtonStyles.GREEN,
                )
            )
        ]
        message = await ctx.channel.send(
            embeds=embed_message("Giveaway", description, "Joined: 0", member=member),
            components=components,
        )

        # push that to the db
        giveaway = BackendGiveaway(ctx=None, discord_guild=ctx.guild, discord_member=member, message_id=message.id)
        await giveaway.create()

        await ctx.send(embeds=embed_message("Success", "The giveaway has been created"), ephemeral=True)


def setup(client):
    Giveaway(client)
