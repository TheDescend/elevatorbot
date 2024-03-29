import random

from naff import CommandTypes, Message, context_menu

from ElevatorBot.commandHelpers.permissionTemplates import restrict_default_permission
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.misc.giveaway import BackendGiveaway
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class GiveawayWinners(BaseModule):
    """
    Close the giveaway and draw a winner from the giveaway. Use multiple times if you want multiple winners
    """

    @context_menu(
        name="Draw Giveaway Winner",
        context_type=CommandTypes.MESSAGE,
        dm_permission=False,
        scopes=get_setting("COMMAND_GUILD_SCOPE"),
    )
    @restrict_default_permission()
    async def draw_winner(self, ctx: ElevatorInteractionContext):
        message: Message = ctx.target

        # get the giveaway data from the db
        giveaway = BackendGiveaway(ctx=ctx, discord_guild=ctx.guild, discord_member=ctx.author, message_id=message.id)
        giveaway.hidden = True
        data = await giveaway.get()

        # error empty ones
        if not data.discord_ids:
            await ctx.send(
                ephemeral=True,
                embeds=embed_message(
                    "Error",
                    "Nobody has entered the giveaway",
                ),
            )
            return

        # draw a winner
        drawn = random.choice(data.discord_ids)
        drawn_member = await ctx.guild.fetch_member(drawn)

        if not drawn_member:
            await ctx.send(
                ephemeral=True,
                embeds=embed_message(
                    "Error",
                    f"{drawn_member} won, but is not in the server anymore",
                ),
            )
            return

        # send that to the DB
        new_data = await giveaway.remove(to_remove=drawn)

        # edit the message and disable the join button
        message.components[0].components[0].disabled = True
        message.embeds[0].footer.text = f"Joined: {len(new_data.discord_ids)}"
        await message.edit(components=message.components, embeds=message.embeds[0])

        await ctx.send(
            embeds=embed_message(
                "🎉 Giveaway Winner 🎉",
                f"{drawn_member.mention} won the [giveaway]({message.jump_url}). Congratulations!",
            ),
        )


def setup(client):
    GiveawayWinners(client)
