from naff import OptionTypes, Role, slash_command, slash_option

from ElevatorBot.commandHelpers.permissionTemplates import restrict_default_permission
from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command, setup_sub_command_clan_group
from ElevatorBot.commands.base import BaseModule
from ElevatorBot.core.misc.persistentMessages import PersistentMessages
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.cache import registered_role_cache
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.networking.destiny.clan import DestinyClan
from ElevatorBot.networking.destiny.profile import DestinyProfile


class ClanRole(BaseModule):
    @slash_command(
        **setup_sub_command,
        **setup_sub_command_clan_group,
        sub_cmd_name="role",
        sub_cmd_description="Designate the role that is given to people that are in the linked clan",
        dm_permission=False,
    )
    @slash_option(
        name="role",
        description="The role to link",
        required=True,
        opt_type=OptionTypes.ROLE,
    )
    @restrict_default_permission()
    async def clan_role(self, ctx: ElevatorInteractionContext, role: Role):
        # cheat a bit and register the role as a persistent message
        persistent_messages = PersistentMessages(ctx=ctx, guild=ctx.guild, message_name="clan_role")
        persistent_messages.hidden = True

        await persistent_messages.upsert(channel_id=role.id)

        await ctx.send(
            embeds=embed_message(
                "Success", f"{role.mention} is now assigned to clan members. I will check this periodically."
            )
        )

        # check all members
        for member in ctx.guild.humans:
            # check if member is not pending
            if not member.pending:
                destiny_profile = DestinyProfile(ctx=ctx, discord_member=member, discord_guild=ctx.guild)
                await destiny_profile.assign_registration_role()

        # get clan members
        destiny_clan = DestinyClan(ctx=None, discord_guild=ctx.guild)
        clan_members = await destiny_clan.get_clan_members()
        clan_members_discord_ids = [member.discord_id for member in clan_members.members if member.discord_id]

        # check all members
        for member in ctx.guild.humans:
            if member.id not in clan_members_discord_ids:
                if member.has_role(role):
                    await member.remove_role(role=role, reason="Destiny2 Clan Membership Update")
            else:
                if not member.has_role(role):
                    await member.add_role(role=role, reason="Destiny2 Clan Membership Update")


def setup(client):
    ClanRole(client)
