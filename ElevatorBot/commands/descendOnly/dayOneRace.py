# from discord.ext.commands import Cog
# from discord_slash import SlashContext, cog_ext
#
# from ElevatorBot.commandHelpers.permissionTemplates import permissions_kigstn
#
#
# class DayOneRace(Cog):
#     def __init__(self, client):
#         self.client = client
#
#     @cog_ext.cog_slash(
#         name="day1race",
#         description="Starts the Day One raid completion announcer",
#         default_permission=False,
#         permissions=permissions_kigstn,
#         scope=COMMAND_GUILD_SCOPE
#     )
#     async def _day1race(self, ctx: SlashContext):
#         pass
#
#
# def setup(client):
#     DayOneRace(client)
