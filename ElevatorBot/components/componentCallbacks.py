from copy import copy

from anyio import to_thread
from dis_snek.models import ComponentContext
from github.GithubObject import NotSet

from ElevatorBot.backendNetworking.destiny.clan import DestinyClan
from ElevatorBot.backendNetworking.github import get_github_repo
from ElevatorBot.backendNetworking.misc.giveaway import BackendGiveaway
from ElevatorBot.backendNetworking.misc.polls import BackendPolls
from ElevatorBot.commands.destiny.registration.register import send_registration
from ElevatorBot.core.destiny.lfg.lfgSystem import LfgMessage
from ElevatorBot.core.misc.poll import Poll
from ElevatorBot.misc.discordShortcutFunctions import assign_roles_to_member, remove_roles_from_member
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.static.descendOnlyIds import descend_channels
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

        # create a poll obj from that data
        poll_obj = await Poll.from_pydantic_model(client=ctx.bot, data=result)
        await poll_obj.send(ctx, user_input=True)

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

        # loop through the roles the user wants (to lose)
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
        embed = embed_message("Role Update", member=ctx.author)
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
            await ctx.send(ephemeral=True, content="Sorry, the game has been won and is over!")
        else:
            embed = ctx.message.embeds[0]
            embed.description = f"Last used by {ctx.author.mention} {custom_emojis.zoom}"

            await ctx.edit_origin(components=[new_component], embeds=embed)

    @staticmethod
    async def lfg_join(ctx: ComponentContext):
        """Handles when a component with the custom_id 'lfg_join' gets interacted with"""

        lfg_message = await LfgMessage.from_component_button(ctx=ctx)
        result = await lfg_message.add_joined(member=ctx.author, ctx=ctx)

        # tell them that it failed
        if not result:
            await ctx.send(
                ephemeral=True,
                embeds=embed_message(
                    "Error", "You could not be added to the event because you are already in it or it is full"
                ),
            )

    @staticmethod
    async def lfg_leave(ctx: ComponentContext):
        """Handles when a component with the custom_id 'lfg_leave' gets interacted with"""

        lfg_message = await LfgMessage.from_component_button(ctx=ctx)
        result = await lfg_message.remove_member(member=ctx.author, ctx=ctx)

        # tell them that it failed
        if not result:
            await ctx.send(
                ephemeral=True,
                embeds=embed_message("Error", "You can't be removed from an event you did not sign up for"),
            )

    @staticmethod
    async def lfg_backup(ctx: ComponentContext):
        """Handles when a component with the custom_id 'lfg_backup' gets interacted with"""

        lfg_message = await LfgMessage.from_component_button(ctx=ctx)
        result = await lfg_message.add_backup(member=ctx.author, ctx=ctx)

        # tell them that it failed
        if not result:
            await ctx.send(
                ephemeral=True,
                embeds=embed_message("Error", "You are already in the backup"),
            )

    @staticmethod
    async def clan_join_request(ctx: ComponentContext):
        """Handles when a component with the custom_id 'clan_join_request' gets interacted with"""

        await ctx.defer()

        # invite them to the clan
        clan = DestinyClan(ctx=ctx, discord_guild=ctx.guild)
        clan.discord_member = ctx.author
        clan.hidden = True
        result = await clan.invite_to_clan(to_invite=ctx.author)

        # send a message in descend if that's the guild
        if ctx.guild == descend_channels.guild:
            embed = embed_message("Clan Update", f"An invite was send to {ctx.author.mention}")
            embed.add_field(name="Bungie Name", value=result.bungie_name, inline=True)
            embed.add_field(name="Destiny ID", value=result.destiny_id, inline=True)
            embed.add_field(name="System", value=result.system, inline=True)

            await descend_channels.bot_dev_channel.send(embeds=embed)

        # inform user if invite was send
        embed = embed_message("Clan Application", "Check your game, I sent you a clan application", member=ctx.author)
        await ctx.send(ephemeral=True, embeds=embed)

    @staticmethod
    async def github(ctx: ComponentContext):
        """Handles when a component with the custom_id 'github' gets interacted with"""

        await ctx.defer(edit_origin=True)

        # close the issue
        issue_id = int(ctx.message.embeds[0].footer.text.split(":")[1].strip())
        repo = await get_github_repo()

        # run those in a thread with anyio since they are blocking
        issue = await to_thread.run_sync(repo.get_issue, issue_id)
        await to_thread.run_sync(issue.edit, NotSet, NotSet, NotSet, "closed")

        # disable the button
        components = copy(ctx.message.components)
        components[1].components[0].disabled = True
        await ctx.edit_origin(components=components)

    @staticmethod
    async def giveaway(ctx: ComponentContext):
        """Handles when a component with the custom_id 'giveaway' gets interacted with"""

        giveaway = BackendGiveaway(
            ctx=ctx, discord_guild=ctx.guild, discord_member=ctx.author, message_id=ctx.message.id
        )
        giveaway.hidden = True
        data = await giveaway.insert()

        # edit the message
        ctx.message.embeds[0].footer.text = f"Joined: {len(data.discord_ids)}"
        await ctx.message.edit(embeds=ctx.message.embeds[0])

        await ctx.send(
            ephemeral=True,
            embeds=embed_message(
                "Success",
                "You have joined the giveaway",
            ),
        )
