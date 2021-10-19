# from discord.ext.commands import Cog
# from discord_slash import cog_ext
# from discord_slash import SlashContext
# from discord_slash.utils.manage_commands import create_choice
# from discord_slash.utils.manage_commands import create_option
#
# from ElevatorBot.commandHelpers.optionTemplates import default_user_option
#
#
# class Time(Cog):
#     def __init__(self, client):
#         self.client = client
#
#     @cog_ext.cog_slash(
#         name="time",
#         description="Shows you your Destiny 2 playtime split up by season",
#         options=[
#             create_option(
#                 name="class",
#                 description="Default: 'Everything' - Which class you want to limit your playtime to",
#                 option_type=3,
#                 required=False,
#                 choices=[
#                     create_choice(name="Everything", value="Everything"),
#                     create_choice(name="Warlock", value="Warlock"),
#                     create_choice(name="Hunter", value="Hunter"),
#                     create_choice(name="Titan", value="Titan"),
#                 ],
#             ),
#             default_user_option(),
#         ],
#     )
#     async def _time(self, ctx: SlashContext, **kwargs):
#         pass
#
#
# def setup(client):
#     Time(client)
