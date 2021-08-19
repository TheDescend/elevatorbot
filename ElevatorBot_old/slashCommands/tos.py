from discord.ext import commands
from discord.http import Route
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice


class ToSCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="discordactivity",
        description="Allows you to use discord activities while in a voice channel",
        options=[
            create_option(
                name="activity",
                description="Select the activity",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name="Youtube Together",
                        value="Youtube Together|755600276941176913",
                    ),
                    create_choice(
                        name="Betrayal.io", value="Betrayal.io|773336526917861400"
                    ),
                    create_choice(
                        name="Fishingtron.io", value="Fishingtron.io|814288819477020702"
                    ),
                    create_choice(
                        name="Poker Night", value="Poker Night|755827207812677713"
                    ),
                    create_choice(
                        name="Chess in the Park",
                        value="Chess in the Park|832012815819604009",
                    ),
                ],
            ),
        ],
    )
    async def _discordactivity(self, ctx: SlashContext, activity: str):
        voice = ctx.author.voice

        activity_name = activity.split("|")[0]
        activity_id = activity.split("|")[1]

        if not voice:
            await ctx.send(
                hidden=True,
                content="You have to be in a voice channel to use this command.",
            )
            return

        r = Route("POST", "/channels/{channel_id}/invites", channel_id=voice.channel.id)

        payload = {
            "max_age": 0,
            "target_type": 2,
            "target_application_id": int(activity_id),
        }

        code = (await self.client.http.request(r, json=payload))["code"]

        await ctx.send(
            content=f"[Click here to join the voice channel and play {activity_name}!](https://discord.gg/{code})"
        )


def setup(client):
    client.add_cog(ToSCommands(client))
