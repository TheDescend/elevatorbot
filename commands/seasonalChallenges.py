from commands.base_command import BaseCommand
from functions.dataLoading import getTriumphsJSON
from functions.dataTransformation import getSeasonalChallengeInfo
from functions.database import lookupDestinyID
from functions.formating import embed_message

import asyncio


class challenges(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Shows you the seasonal challenges and your completion status"
        params = ["*week 1|2|3..."]
        topic = "Destiny"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client, old_message=None, seasonal_challenges=None, week=None):
        async with message.channel.typing():
            # recursive commmand. if this is the first time this command is called get the data
            if not old_message:
                # get seasonal challenge info
                seasonal_challenges = await getSeasonalChallengeInfo()
                index = list(seasonal_challenges)

                # get the week (or the default - whatever is first)
                week = f"Week {params[0]}" if params else ""
                if week not in seasonal_challenges:
                    week = index[0]

            else:
                index = list(seasonal_challenges)

            embed = embed_message(
                f"{mentioned_user.display_name}'s Seasonal Challenges - {week}"
            )

            # add the triumphs and what the user has done
            destinyID = lookupDestinyID(mentioned_user.id)
            user_triumphs = await getTriumphsJSON(destinyID)
            for triumph in seasonal_challenges[week]:
                user_triumph = user_triumphs[str(triumph["referenceID"])]

                # calculate completion rate
                rate = []
                for objective in user_triumph["objectives"]:
                    rate.append(objective["progress"] / objective["completionValue"] if not objective["complete"] else 1)
                rate = sum(rate) / len(rate)

                # make emoji art for completion rate
                rate_text = "|"
                if rate > 0:
                    rate_text += "🟩"
                else:
                    rate_text += "🟥"
                if rate > 0.25:
                    rate_text += "🟩"
                else:
                    rate_text += "🟥"
                if rate > 0.5:
                    rate_text += "🟩"
                else:
                    rate_text += "🟥"
                if rate == 1:
                    rate_text += "🟩"
                else:
                    rate_text += "🟥"
                rate_text += "|"

                # add field to embed
                embed.add_field(name=f"""{triumph["name"]} {rate_text}""", value=triumph["description"], inline=False)

        # send message
        if not old_message:
            old_message = await message.reply(embed=embed)
        else:
            await old_message.edit(embed=embed)

        # get current indexes - to look whether to add arrows to right
        current_index = index.index(week)
        max_index = len(index) - 1

        # add reactions
        if current_index > 0:
            await old_message.add_reaction("⬅")
        if current_index < max_index:
            await old_message.add_reaction("➡")

        # wait 60s for reaction
        def check(reaction_reaction, reaction_user):
            return (str(reaction_reaction.emoji) == "⬅" or str(reaction_reaction.emoji) == "➡") \
                   and (reaction_reaction.message.id == old_message.id) \
                   and (message.author == reaction_user)
        try:
            reaction, _ = await client.wait_for('reaction_add', check=check, timeout=60)
        except asyncio.TimeoutError:
            # clear reactions
            await old_message.clear_reactions()
        else:
            # clear reactions
            await old_message.clear_reactions()

            # recursively call this function
            new_index = index[current_index - 1] if str(reaction.emoji) == "⬅" else index[current_index + 1]
            new_call = challenges()
            await new_call.handle(params, message, mentioned_user, client, old_message, seasonal_challenges, new_index)
