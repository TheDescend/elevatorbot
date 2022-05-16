# all credit goes to @LordOfPolls - https://github.com/Discord-Snake-Pit/Dis-Secretary
import asyncio
import re
import textwrap

import aiohttp
import github
from naff import Message

from ElevatorBot.misc.formatting import embed_message


class GitHubManager:
    snippet_regex = re.compile(r"github\.com/([\w\-_]+)/([\w\-_]+)/blob/([\w\-_]+)/([\w\-_/.]+)(#L[\d]+(-L[\d]+)?)?")

    @staticmethod
    async def reply(message: Message, **kwargs):
        await message.suppress_embeds()
        await message.reply(**kwargs)

    @staticmethod
    async def get_pull(repo, pr_id: int):
        try:
            pr = await asyncio.to_thread(repo.get_pull, pr_id)
            return pr

        except github.UnknownObjectException:
            return None

    @staticmethod
    async def get_issue(repo, issue_id: int):
        try:
            issue = await asyncio.to_thread(repo.get_issue, issue_id)
            return issue

        except github.UnknownObjectException:
            return None

    @staticmethod
    def assemble_body(body: str, max_lines=10):
        """Cuts the body of an issue / pr to fit nicely"""
        output = []
        body = (body or "No Description Given").split("\n")

        start = 0
        for i in range(len(body)):
            if body[i].startswith("## Description"):
                start = i + 1

            if body[i].startswith("## Checklist"):
                body = body[:i]
                break
        code_block = False

        for i in range(len(body)):
            if i < start:
                continue

            line = body[i].strip("\r")
            if line in ["", "\n", " "] or line.startswith("!image"):
                continue
            if line.startswith("## "):
                line = f"**{line[3:]}**"

            # try and remove code blocks
            if line.strip().startswith("```"):
                if not code_block:
                    code_block = True
                    continue
                else:
                    code_block = False
                    continue
            if not code_block:
                output.append(line)
            if len(output) == max_lines:
                # in case a code block got through, make sure its closed
                if "".join(output).count("```") % 2 != 0:
                    output.append("```")
                output.append(f"`... and {len(body) - i} more lines`")
                break

        return "\n".join(output)

    async def send_pr(self, message: Message, pr):
        """Send a reply to a message with a formatted pr"""
        embed = embed_message(title=f"PR #{pr.number}: {pr.title}")
        embed.url = pr.html_url
        embed.set_footer(
            text=f"{pr.user.name if pr.user.name else pr.user.login} - {pr.created_at.ctime()}",
            icon_url=pr.user.avatar_url,
        )

        if pr.state == "closed":
            if pr.merged:
                embed.description = f"💜 Merged by {pr.merged_by.name} at {pr.merged_at.ctime()}"
            else:
                embed.description = "🚫 Closed"
        if pr.state == "open":
            embed.description = "🟢 Open"

        body = re.sub(r"<!--?.*-->", "", pr.body)

        embed.description += (
            f"{' - ' if len(pr.labels) != 0 else ''}{', '.join(f'``{l.name.capitalize()}``' for l in pr.labels)}\n"
            f"{self.assemble_body(body, max_lines=5)}"
        )

        if body and "## What type of pull request is this?" in body:
            lines = []
            copy = False
            for line in body.split("\n"):
                if "## What type of pull request is this?" in line.strip():
                    copy = True
                if "## Description" in line.strip():
                    copy = False
                if copy:
                    lines.append(line)
            pr_type = re.sub("\[[^\s]]", "✅", "\n".join(lines[1:]))
            pr_type = pr_type.replace("[ ]", "❌")
            embed.add_field(name="PR Type", value=pr_type)

        if body and "## Checklist" in body:
            checklist = body.split("## Checklist")[-1].strip("\r")
            checklist = re.sub("\[[^\s]]", "✅", checklist)
            checklist = checklist.replace("[ ]", "❌")
            embed.add_field(name="Checklist", value=checklist)

        if not pr.merged:
            embed.add_field(name="Mergeable", value=pr.mergeable_state, inline=False)

        await self.reply(message, embeds=embed)

    async def send_issue(self, message: Message, issue):
        """Send a reply to a message with a formatted issue"""
        embed = embed_message(title=f"Issue #{issue.number}: {issue.title}")
        embed.url = issue.html_url
        embed.set_footer(
            text=f"{issue.user.name if issue.user.name else issue.user.login}",
            icon_url=issue.user.avatar_url,
        )

        if issue.state == "closed":
            embed.description = "🚫 Closed"
        if issue.state == "open":
            if issue.locked:
                embed.description = "🔒 Locked"
            else:
                embed.description = "🟢 Open"

        body = re.sub(r"<!--?.*-->", "", issue.body if issue.body else "_Empty_")

        embed.description += (
            f"{' - ' if len(issue.labels) != 0 else ''}{', '.join(f'``{l.name.capitalize()}``' for l in issue.labels)}\n"
            f"{self.assemble_body(body)}"
        )

        await self.reply(message, embeds=embed)

    async def send_snippet(self, message: Message):
        results = self.snippet_regex.findall(message.content)[0]

        lines = [int(re.sub("[^0-9]", "", line)) for line in results[4].split("-")] if len(results) >= 5 else None
        if not lines:
            return
        user = results[0]
        repo = results[1]
        branch = results[2]
        file = results[3]
        extension = file.split(".")[-1]

        raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file}"

        async with aiohttp.ClientSession() as session:
            async with session.get(raw_url) as resp:
                if resp.status != 200:
                    return

                file_data = await resp.text()
                if file_data and lines:
                    lines[0] -= 1  # account for 0 based indexing
                    sample = file_data.split("\n")
                    if len(lines) == 2:
                        sample = sample[lines[0] :][: lines[1] - lines[0]]
                        file_data = "\n".join(sample)
                    else:
                        file_data = sample[lines[0]]

                embed = embed_message(
                    title=f"{user}/{repo}",
                    description=f"```{extension}\n{textwrap.dedent(file_data)}```",
                )

                await self.reply(message, embeds=embed)


github_manager = GitHubManager()
