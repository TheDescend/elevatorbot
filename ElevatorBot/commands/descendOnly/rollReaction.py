# from discord.ext.commands import Cog
# from discord_slash import SlashContext, cog_ext
# from discord_slash.utils.manage_commands import create_option
#
# from ElevatorBot.commandHelpers.permissionTemplates import permissions_admin
#
#
# class RollReaction(Cog):
#     def __init__(self, client):
#         self.client = client
#
#     @cog_ext.cog_slash(
#         name="rollreaction",
#         description="Picks a random reactor from the post above",
#         options=[
#             create_option(
#                 name="draws",
#                 description="How many people to draw",
#                 option_type=4,
#                 required=True,
#             ),
#         ],
#         default_permission=False,
#         permissions=permissions_admin, scope=COMMAND_GUILD_SCOPE
#     )
#     async def _rollreaction(self, ctx: SlashContext, draws: int):
#         pass
#
#
# def setup(client):
#     RollReaction(client)
