from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from ElevatorBot.database.database import removeUser, setSteamJoinID, getSteamJoinID
from ElevatorBot.core.clanJoinRequests import elevatorRegistration
from ElevatorBot.core.formating import embed_message
from ElevatorBot.core.persistentMessages import steamJoinCodeMessage
from ElevatorBot.core.slashCommandFunctions import get_user_obj_admin, get_user_obj
from ElevatorBot.static.slashCommandOptions import options_user


class RegistrationCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="registerdesc",
        description="Link your Destiny 2 account with ElevatorBot",
    )
    async def _registerdesc(self, ctx: SlashContext):
        if not ctx.guild:
            await ctx.author.send("Please use this command in your clans bot-channel")
            return

        await ctx.send(
            hidden=True,
            embed=embed_message(
                f"Thanks for Registering", f"I sent you a DM with the next steps!"
            ),
        )

        await elevatorRegistration(ctx.author)

    @cog_ext.cog_slash(
        name="unregisterdesc",
        description="Unlink your Destiny 2 account from ElevatorBot",
        options=[options_user(flavor_text="Requires elevated permissions")],
    )
    async def _unregisterdesc(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj_admin(ctx, kwargs)
        if not user:
            return

        await removeUser(user.id)
        await ctx.send(
            hidden=True, embed=embed_message(f"Sucess", f"Removed {user.display_name}")
        )

    # todo can we add a good permission sysstem here too?
    @cog_ext.cog_subcommand(
        base="id",
        base_description="Steam IDs which can be used to join people in Destiny 2 without adding them as a friend",
        name="get",
        description="Get a Steam ID",
        options=[options_user()],
    )
    async def _get(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)

        text = await getSteamJoinID(user.id)
        if not text:
            text = "Nothing found. Please tell the user to set the code with \n`/id set <code>`\nYou can find your own code by typing `/id` in-game\n⁣\nSadly I do not have access to this information, since it is handled by Steam and not Bungie"
        else:
            text = f"/join {text}"

        embed = embed_message(f"{user.display_name}'s Steam Join Code", f"{text}")
        await ctx.send(embed=embed)

    # todo can we add a good permission sysstem here too?
    @cog_ext.cog_subcommand(
        base="id",
        base_description="Steam IDs which can be used to join people in Destiny 2 without adding them as a friend",
        name="set",
        description="Set your Steam ID",
        options=[
            create_option(
                name="steamid",
                description="Your Steam ID which you want to set",
                option_type=3,
                required=True,
            ),
            options_user(flavor_text="Requires elevated permissions"),
        ],
    )
    async def _set(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj_admin(ctx, kwargs)
        if not user:
            return

        # check if id is an int
        try:
            kwargs["steamid"] = int(kwargs["steamid"])
        except ValueError:
            await ctx.send(
                hidden=True,
                embed=embed_message(
                    f"Error",
                    f"The argument `steamid` must be a number. \nPlease try again",
                ),
            )
            return

        # save id
        await setSteamJoinID(user.id, kwargs["steamid"])

        # _update the status msg
        await steamJoinCodeMessage(self.client, ctx.guild)

        # react to show that it is done
        await ctx.send(
            hidden=True, embed=embed_message(f"Success", f"I've done as you asked")
        )


def setup(client):
    client.add_cog(RegistrationCommands(client))
