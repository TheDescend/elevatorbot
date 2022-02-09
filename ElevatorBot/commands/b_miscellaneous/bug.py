from typing import Optional

from anyio import to_thread
from dis_snek import (
    ActionRow,
    Attachment,
    Button,
    ButtonStyles,
    InteractionContext,
    OptionTypes,
    slash_command,
    slash_option,
)
from github.GithubObject import NotSet

from ElevatorBot.backendNetworking.github import get_github_labels, get_github_repo
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.static.descendOnlyIds import descend_channels


class Bug(BaseScale):
    @slash_command(name="bug", description="Use this if you want to report any bugs to the developer")
    @slash_option(
        name="message",
        description="Please describe **in detail** the bug you have noticed",
        opt_type=OptionTypes.STRING,
        required=True,
    )
    @slash_option(
        name="image",
        description="An image of the problem (press `win` + `shift` + `s`)",
        opt_type=OptionTypes.ATTACHMENT,
        required=False,
    )
    async def bug(self, ctx: InteractionContext, message: str, image: Optional[Attachment]):
        if not image:
            image = "_No Image Provided_"

        components = None
        embed = embed_message("Bug Report", f"{message}\n⁣\n- by {ctx.author.mention}", member=ctx.author)

        # upload that to GitHub
        repo = await get_github_repo()
        if repo:
            # run those in a thread with anyio since they are blocking
            issue = await to_thread.run_sync(
                repo.create_issue,
                f"Bug Report by Discord User `{ctx.author.username}#{ctx.author.discriminator}`",
                f"{image.url}\n⁣\n{message}\n⁣\n_This action was performed automatically by a bot_",
                NotSet,
                NotSet,
                await get_github_labels(),
            )

            components = [
                ActionRow(
                    Button(style=ButtonStyles.URL, label="View the Bug Report", url=issue.html_url),
                ),
                ActionRow(
                    Button(custom_id="github", style=ButtonStyles.GREEN, label="Close Issue"),
                ),
            ]
            embed.set_footer(f"ID: {issue.number}")

        # send that in the bot dev channel
        await descend_channels.bot_dev_channel.send(embeds=embed, components=components)

        await ctx.send(
            ephemeral=True,
            embeds=embed_message(
                "Success",
                "Your message has been forwarded to my developer\nDepending on the clarity of your bug report, you may or may not be contacted by them",
            ),
            components=components[:1],
        )


def setup(client):
    Bug(client)
