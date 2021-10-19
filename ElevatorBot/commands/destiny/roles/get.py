# from discord.ext.commands import Cog
# from discord_slash import cog_ext
# from discord_slash import SlashContext
#
# from ElevatorBot.commandHelpers.decorators import has_user_option_permission
# from ElevatorBot.commandHelpers.optionTemplates import default_user_option
#
#
# class RoleGet(Cog):
#     def __init__(self, client):
#         self.client = client
#
#     @cog_ext.cog_subcommand(
#         base="roles",
#         base_description="Various commands concerning Destiny 2 achievement discord roles",
#         name="get",
#         description="Assigns you all the roles you've earned",
#         options=[default_user_option(description="Requires elevated permissions")],
#     )
#     @has_user_option_permission
#     async def _roles_get(self, ctx: SlashContext, **kwargs):
#         pass
#
#
# def setup(client):
#     RoleGet(client)
