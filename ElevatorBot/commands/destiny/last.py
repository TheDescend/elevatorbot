# from discord.ext.commands import Cog
# from discord_slash import cog_ext
# from discord_slash import SlashContext
# from discord_slash.utils.manage_commands import create_option
#
# from ElevatorBot.commandHelpers.optionTemplates import default_user_option
# from ElevatorBot.commandHelpers.optionTemplates import get_mode_choices
#
#
# class Last(Cog):
#     def __init__(self, client):
#         self.client = client
#
#     @cog_ext.cog_slash(
#         name="last",
#         description="Stats for the last activity you played",
#         options=[
#             create_option(
#                 name="activity",
#                 description="The type of the activity",
#                 option_type=3,
#                 required=True,
#                 choices=get_mode_choices(),
#             ),
#             default_user_option(),
#         ],
#     )
#     async def _last(self, ctx: SlashContext, **kwargs):
#         pass
#
#
# def setup(client):
#     Last(client)
