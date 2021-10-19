# from discord.ext.commands import Cog
# from discord_slash import cog_ext
# from discord_slash import SlashContext
#
# from ElevatorBot.commandHelpers.optionTemplates import default_user_option
#
#
# class SeasonalChallenges(Cog):
#     def __init__(self, client):
#         self.client = client
#
#     @cog_ext.cog_slash(
#         name="challenges",
#         description="Shows you the seasonal challenges and your completion status",
#         options=[default_user_option()],
#     )
#     async def _challenges(self, ctx: SlashContext, **kwargs):
#         pass
#
#
# def setup(client):
#     SeasonalChallenges(client)
