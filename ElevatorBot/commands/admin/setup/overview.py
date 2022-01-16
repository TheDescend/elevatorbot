from dis_snek.models import InteractionContext, slash_command

from ElevatorBot.backendNetworking.destiny.clan import DestinyClan
from ElevatorBot.commandHelpers.subCommandTemplates import setup_sub_command
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.misc.persistentMessages import PersistentMessages
from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.descendOnlyIds import descend_channels
from Shared.NetworkingSchemas.misc.persistentMessages import PersistentMessage


class Overview(BaseScale):

    # todo perms
    @slash_command(
        **setup_sub_command,
        sub_cmd_name="overview",
        sub_cmd_description="Gives you an overview over my setting for this server",
    )
    async def overview(self, ctx: InteractionContext):
        backend = PersistentMessages(ctx=ctx, guild=ctx.guild, message_name=None)
        result = await backend.get_all()

        # sort them into a handy dictionary to make lookups by key
        handy_dict: dict[str, PersistentMessage] = {}
        for message in result.messages:
            handy_dict.update({message.message_name: message})

        # format the embed
        embed = embed_message(f"{ctx.guild.name}'s Settings")

        clan = DestinyClan(ctx=None, discord_guild=ctx.guild)
        clan_info = await clan.get_clan()
        embed.add_field(name="Linked Clan", value=f"`{clan_info.name}`" if clan_info else "Not Set-Up", inline=True)

        obj = handy_dict["clan_join_request"] if "clan_join_request" in handy_dict else None
        embed.add_field(
            name="Clan Join Button",
            value=f"[Click To View The Linked Message](https://canary.discord.com/channels/{obj.guild_id}/{obj.channel_id}/{obj.message_id})"
            if obj
            else "Not Set-Up",
            inline=True,
        )

        obj = handy_dict["lfg_channel"] if "lfg_channel" in handy_dict else None
        embed.add_field(
            name="LFG Event Channel",
            value=f"<#{obj.channel_id}>" if obj else "Not Set-Up",
            inline=False,
        )

        obj = handy_dict["lfg_voice_category"] if "lfg_voice_category" in handy_dict else None
        embed.add_field(
            name="LFG Event Voice Category",
            value=f"<#{obj.channel_id}>" if obj else "Not Set-Up",
            inline=True,
        )

        obj = handy_dict["rss"] if "rss" in handy_dict else None
        embed.add_field(
            name="Bungie RSS Feed Channel",
            value=f"<#{obj.channel_id}>" if obj else "Not Set-Up",
            inline=False,
        )

        obj = handy_dict["increment_button"] if "increment_button" in handy_dict else None
        embed.add_field(
            name="Increment Button",
            value=f"[Click To View The Linked Message](https://canary.discord.com/channels/{obj.guild_id}/{obj.channel_id}/{obj.message_id})"
            if obj
            else "Not Set-Up",
            inline=True,
        )

        obj = handy_dict["registered_role"] if "registered_role" in handy_dict else None
        embed.add_field(
            name="Registered Role",
            value=f"<@&{obj.channel_id}>" if obj else "Not Set-Up",
            inline=False,
        )

        obj = handy_dict["registration"] if "registration" in handy_dict else None
        embed.add_field(
            name="Registration Button",
            value=f"[Click To View The Linked Message](https://canary.discord.com/channels/{obj.guild_id}/{obj.channel_id}/{obj.message_id})"
            if obj
            else "Not Set-Up",
            inline=True,
        )

        # descend only stuff
        # only add this when the server is descend
        if ctx.guild == descend_channels.guild:
            obj = handy_dict["booster_count"] if "booster_count" in handy_dict else None
            embed.add_field(
                name="Booster Count Channel",
                value=f"<#{obj.channel_id}>" if obj else "Not Set-Up",
                inline=False,
            )

            obj = handy_dict["member_count"] if "member_count" in handy_dict else None
            embed.add_field(
                name="Member Count Channel",
                value=f"<#{obj.channel_id}>" if obj else "Not Set-Up",
                inline=True,
            )

            obj = handy_dict["other_game_roles"] if "other_game_roles" in handy_dict else None
            embed.add_field(
                name="Miscellaneous Roles Message",
                value=f"[Click To View The Linked Message](https://canary.discord.com/channels/{obj.guild_id}/{obj.channel_id}/{obj.message_id})"
                if obj
                else "Not Set-Up",
                inline=False,
            )

            obj = handy_dict["status"] if "status" in handy_dict else None
            embed.add_field(
                name="ElevatorBot Status Message",
                value=f"[Click To View The Linked Message](https://canary.discord.com/channels/{obj.guild_id}/{obj.channel_id}/{obj.message_id})"
                if obj
                else "Not Set-Up",
                inline=True,
            )

        await ctx.send(embeds=embed)


def setup(client):
    Overview(client)
