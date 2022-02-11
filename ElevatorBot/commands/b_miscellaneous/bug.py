import asyncio

from anyio import to_thread
from dis_snek import (
    ActionRow,
    Attachment,
    Button,
    ButtonStyles,
    InteractionContext,
    Modal,
    OptionTypes,
    ParagraphText,
    ShortText,
    slash_command,
    slash_option,
)
from github.GithubObject import NotSet

from ElevatorBot.backendNetworking.github import get_github_labels, get_github_repo
from ElevatorBot.commandHelpers.responseTemplates import respond_timeout
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.misc.formatting import embed_message
from ElevatorBot.static.descendOnlyIds import descend_channels
from Shared.functions.readSettingsFile import get_setting

# =============
# Descend Only!
# =============


class Bug(BaseScale):
    @slash_command(
        name="bug",
        description="Use this if you want to report any bugs to the developer",
        scopes=get_setting("COMMAND_GUILD_SCOPE"),
    )
    @slash_option(
        name="image",
        description="An image of the problem (press `win` + `shift` + `s`)",
        opt_type=OptionTypes.ATTACHMENT,
        required=False,
    )
    async def bug(self, ctx: InteractionContext, image: Attachment = None):
        affected_text = "What command / part of me is affected"
        description_text = "Please describe the bug in detail"
        wanted_text = "What did you want to happen"
        got_text = "What did actually happen"

        # ask the message
        modal = Modal(
            title="Bug Report",
            components=[
                ShortText(
                    label=affected_text,
                    custom_id="affected",
                    placeholder="Required",
                    required=True,
                ),
                ParagraphText(
                    label=description_text,
                    custom_id="description",
                    placeholder="Required",
                    min_length=20,
                    required=True,
                ),
                ParagraphText(
                    label=wanted_text,
                    custom_id="wanted",
                    placeholder="Required",
                    min_length=5,
                    required=True,
                ),
                ParagraphText(
                    label=got_text,
                    custom_id="got",
                    placeholder="Required",
                    min_length=5,
                    required=True,
                ),
            ],
        )
        await ctx.send_modal(modal=modal)

        # wait 10 minutes for them to fill it out
        try:
            modal_ctx = await ctx.bot.wait_for_modal(modal=modal, timeout=600)

        except asyncio.TimeoutError:
            # give timeout message
            await respond_timeout(ctx=ctx)
            return

        if not image:
            image = "_No Image Provided_"

        affected = modal_ctx.responses["affected"]
        description = modal_ctx.responses["description"]
        wanted = modal_ctx.responses["wanted"]
        got = modal_ctx.responses["got"]

        components = None
        embed = embed_message("Bug Report", f"Affected: `{affected}`\n⁣\n- by {ctx.author.mention}", member=ctx.author)

        # upload that to GitHub
        repo = await get_github_repo()
        if repo:
            # run those in a thread with anyio since they are blocking
            issue = await to_thread.run_sync(
                repo.create_issue,
                f"Bug Report by Discord User `{ctx.author.username}#{ctx.author.discriminator}`",
                f"### Image\n{image.url}\n⁣\n### {affected_text}\n```{affected}```\n⁣\n### {description_text}\n```{description}```\n⁣\n### {wanted_text}\n```{wanted}```\n⁣\n### {got_text}\n```{got}```\n⁣\n⁣\n_This action was performed automatically by a bot_",
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

        await modal_ctx.send(
            ephemeral=True,
            embeds=embed_message(
                "Success",
                "Your message has been forwarded to my developer\nDepending on the clarity of your bug report, you may or may not be contacted by them",
            ),
            components=components[:1],
        )


def setup(client):
    Bug(client)
