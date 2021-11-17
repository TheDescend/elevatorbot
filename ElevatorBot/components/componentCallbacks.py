from copy import copy

from dis_snek.models import ActionRow, Button, ButtonStyles, ComponentContext

from Backend.database.models import Poll
from ElevatorBot.backendNetworking.misc.polls import BackendPolls
from ElevatorBot.commands.destiny.registration.register import send_registration
from ElevatorBot.misc.discordShortcutFunctions import (
    assign_roles_to_member,
    remove_roles_from_member,
)
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.emojis import custom_emojis


class ComponentCallbacks:
    @staticmethod
    async def poll(ctx: ComponentContext):
        """Handles when a component with the custom_id 'poll' gets interacted with"""

        backend = BackendPolls(ctx=ctx, discord_member=ctx.author, guild=ctx.guild)
        backend.hidden = True

        # get the id from the embed
        poll_id = int(ctx.message.embeds[0].footer.text.split("|")[1].removeprefix("  ID: "))

        # inform the db that sb voted
        result = await backend.user_input(poll_id=poll_id, choice_name=ctx.values[0])

        if not result:
            return

        # create a poll obj from that data
        poll_obj = await Poll.from_dict(client=ctx.bot, data=result)
        await poll_obj.send(ctx)

    @staticmethod
    async def registration(ctx: ComponentContext):
        """Handles when a component with the custom_id 'registration' gets interacted with"""

        # send them the message
        await send_registration(ctx)

    @staticmethod
    async def other_game_roles(ctx: ComponentContext):
        """Handles when a component with the custom_id 'other_game_roles' gets interacted with"""

        # assign or remove the wanted roles
        user_role_ids = [role.id for role in ctx.author.roles]

        added = []
        removed = []

        # loop through the roles the user wants (to loose)
        for role in ctx.values:
            role_name, role_id = role.split("|")
            role_id = int(role_id)

            # add role
            if role_id not in user_role_ids:
                await assign_roles_to_member(ctx.author, role_id, reason="Other Game Roles")
                added.append(role_name)

            # delete role
            else:
                await remove_roles_from_member(ctx.author, role_id, reason="Other Game Roles")
                removed.append(role_name)

        # send message to user
        embed = embed_message(
            f"Role Update",
        )
        if added:
            embed.add_field(name="Roles Added", value="\n".join(added), inline=True)
        if removed:
            embed.add_field(name="Roles Removed", value="\n".join(removed), inline=True)

        await ctx.send(ephemeral=True, embeds=embed)

    @staticmethod
    async def increment_button(ctx: ComponentContext):
        """Handles when a component with the custom_id 'increment_button' gets interacted with"""

        # increment the button by 1
        new_component = copy(ctx.message.components[0])
        label = str(int(new_component.components[0].label) + 1)
        new_component.components[0].label = label

        if int(label) == 69420:
            await ctx.send(ephemeral=True, content=f"Sorry, the game has been won and is over!")
        else:
            embed = ctx.message.embeds[0]
            embed.description = f"Last used by {ctx.author.mention} {custom_emojis.zoom}"

            await ctx.edit_origin(components=[new_component], embeds=embed)

    @staticmethod
    async def lfg_join(ctx: ComponentContext):
        """Handles when a component with the custom_id 'lfg_join' gets interacted with"""

        # todo
        lfg_message = await get_lfg_message(client=ctx.bot, lfg_message_id=ctx.origin_message.id, guild=ctx.guild)
        if not lfg_message:
            return

        res = await lfg_message.add_member(member=ctx.guild.get_member(ctx.author.id), ctx=ctx)
        if not res:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Error",
                    "You could not be added to the event\nThis is either because you are already in the event, the event is full, or the creator has "
                    "blacklisted you from their events",
                ),
            )

    @staticmethod
    async def lfg_leave(ctx: ComponentContext):
        """Handles when a component with the custom_id 'lfg_leave' gets interacted with"""

        # todo
        lfg_message = await get_lfg_message(client=ctx.bot, lfg_message_id=ctx.origin_message.id, guild=ctx.guild)
        if not lfg_message:
            return

        res = await lfg_message.remove_member(member=ctx.guild.get_member(ctx.author.id), ctx=ctx)
        if not res:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Error",
                    "You could not be removed from the event\nThis is because you are neither in the main nor in the backup roster",
                ),
            )

    @staticmethod
    async def lfg_backup(ctx: ComponentContext):
        """Handles when a component with the custom_id 'lfg_backup' gets interacted with"""

        # todo
        lfg_message = await get_lfg_message(client=ctx.bot, lfg_message_id=ctx.origin_message.id, guild=ctx.guild)
        if not lfg_message:
            return

        res = await lfg_message.add_backup(member=ctx.guild.get_member(ctx.author.id), ctx=ctx)
        if not res:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    "Error",
                    "You could not be added as a backup to the event\nThis is either because you are already in the backup roster, or the creator has "
                    "blacklisted you from their events",
                ),
            )

    @staticmethod
    async def clan_join_request(ctx: ComponentContext):
        """Handles when a component with the custom_id 'clan_join_request' gets interacted with"""

        # todo
        await on_clan_join_request(ctx)
