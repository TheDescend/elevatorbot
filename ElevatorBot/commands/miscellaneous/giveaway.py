from dis_snek import ActionRow, Button, ButtonStyles, Member, OptionTypes, slash_option
from dis_snek.models import InteractionContext, slash_command

from ElevatorBot.backendNetworking.misc.giveaway import BackendGiveaway
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formating import embed_message
from settings import COMMAND_GUILD_SCOPE

# =============
# Descend Only!
# =============


class Giveaway(BaseScale):
    # todo perm
    @slash_command(name="giveaway", description="Creates a giveaway", scopes=COMMAND_GUILD_SCOPE)
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
            embeds=embed_message(f"Giveaway From {member.display_name}", description, "Joined: 0"),
            components=components,
        )

        # push that to the db
        giveaway = BackendGiveaway(ctx=None, discord_guild=ctx.guild, discord_member=member, message_id=message.id)
        await giveaway.create()

        await ctx.send(embeds=embed_message("Success", "The giveaway has been created"), ephemeral=True)
        # todo maybe context menu to draw winners once done


def setup(client):
    Giveaway(client)
