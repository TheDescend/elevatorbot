from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from functions.database import removeUser, setSteamJoinID, getSteamJoinID
from functions.formating import embed_message
from functions.persistentMessages import steamJoinCodeMessage
from functions.slashCommandFunctions import get_user_obj_admin, get_user_obj
from static.config import GUILD_IDS, BUNGIE_OAUTH


class RegistrationCommands(commands.Cog):
    def __init__(self, client):
        self.client = client


    @cog_ext.cog_slash(
        name="registerdesc",
        description="Link your Destiny 2 account with ElevatorBot",
        guild_ids=GUILD_IDS,
    )
    async def _registerdesc(self, ctx: SlashContext):
        await ctx.send("Thanks, I sent you a DM with the next steps!", hidden=True)

        URL = f"https://www.bungie.net/en/oauth/authorize?client_id={BUNGIE_OAUTH}&response_type=code&state={str(ctx.author.id) + ':' + str(ctx.guild.id)}"
        await ctx.author.send(embed=embed_message(
            f'Registration',
            f'[Click here to register with me]({URL})',
            "Please be aware that I will need a while to process your data after you register for the first time, so I might react very slow to your first commands."
        ))


    @cog_ext.cog_slash(
        name="unregisterdesc",
        description="Unlink your Destiny 2 account from ElevatorBot",
        guild_ids=GUILD_IDS,
        options=[
            create_option(
                name="user",
                description="Requires elevated permissions",
                option_type=6,
                required=False
            )
        ]
    )
    async def _unregisterdesc(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj_admin(ctx, kwargs)
        if not user:
            return

        if removeUser(user.id):
            await ctx.send(f'Removed {user.display_name}', hidden=True)
        else:
            await ctx.send(f'Removal failed for {user.display_name}. Please send me a DM to get in touch with my developers', hidden=True)


    # todo can we add a good permission sysstem here too?
    @cog_ext.cog_subcommand(
        base="id",
        base_description="Steam IDs which can be used to join people in Destiny 2 without adding them as a friend",
        name="get",
        description="Get a Steam ID",
        options=[
            create_option(
                name="user",
                description="The user you want to look up",
                option_type=6,
                required=False
            )
        ]
    )
    async def _get(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj(ctx, kwargs)

        text = getSteamJoinID(user.id)
        if not text:
            text = "Nothing found. Please tell the user to set the code with \n`!setID <code>`\nYou can find your own code by typing `/id` in-game\n⁣\nSadly I do not have access to this information, since it is handled by Steam and not Bungie"

        embed = embed_message(
            f"{user.display_name}'s Steam Join Code",
            f"/join {text}"
        )
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
                required=True
            ),
            create_option(
                name="user",
                description="Requires elevated permissions",
                option_type=6,
                required=False
            )
        ]
    )
    async def _set(self, ctx: SlashContext, **kwargs):
        user = await get_user_obj_admin(ctx, kwargs)
        if not user:
            return

        # save id
        setSteamJoinID(user.id, kwargs["steamid"])

        # update the status msg
        await steamJoinCodeMessage(self.client, ctx.guild)

        # react to show that it is done
        await ctx.send("Done, thanks!", hidden=True)



def setup(client):
    client.add_cog(RegistrationCommands(client))
