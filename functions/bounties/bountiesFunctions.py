from functions.formating import embed_message

import os
import pickle
import discord



def giveOutBounties(client):
    pass
    # give all signed up members their bounties, maybe every week, as a dm?
    # that'd be a way to have it run weekly https://stackoverflow.com/questions/43670224/python-to-run-a-piece-of-code-at-a-defined-time-every-day

def startTournament():
    pass


""" 
file = {
    "guild_id": id,
    "register_channel": channel.id,
    "register_channel_message_id": message.id,
    "leaderboard_channel": channel.id,
    "leaderboard_channel_message_id": message.id,
    "bounties_channel": channel.id,
    "tournament_channel: channel.id"
}
"""
def saveAsGlobalVar(name, value, guild_id = None):
    if not os.path.exists('functions/bounties/channelIDs.pickle'):
        file = {}
    else:
        with open('functions/bounties/channelIDs.pickle', "rb") as f:
            file = pickle.load(f)

    if guild_id:
        file["guild_id"] = guild_id
    file[name] = value

    with open('functions/bounties/channelIDs.pickle', "wb") as f:
        pickle.dump(file, f)


def deleteFromGlobalVar(name):
    if os.path.exists('functions/bounties/channelIDs.pickle'):
        with open('functions/bounties/channelIDs.pickle', "rb") as f:
            file = pickle.load(f)

        try:
            file.pop(name)
        except:
            pass

        with open('functions/bounties/channelIDs.pickle', "wb") as f:
            pickle.dump(file, f)


# todo: add leaderboard lookup and calculation
def leaderboardMessage():

    embed = embed_message(
        f'Leaderboard',
        f'ToDo',
        f"The leaderboard will update every 60 minutes"
    )

    return embed


async def updateLeaderboard(client):
    with open('functions/bounties/channelIDs.pickle', "rb") as f:
        file = pickle.load(f)

    for guild in client.guilds:
        if guild.id == file["guild_id"]:
            embed = leaderboardMessage()
            channel = discord.utils.get(guild.channels, id=file["leaderboard_channel"])

            if "leaderboard_channel_message_id" not in file:
                msg = await channel.send(embed=embed)
                saveAsGlobalVar("leaderboard_channel_message_id", msg.id)

            else:
                msg = await channel.fetch_message(file["leaderboard_channel_message_id"])
                await msg.edit(embed=embed)

            return


async def bountiesChannelMessage(client):
    if os.path.exists('functions/bounties/channelIDs.pickle'):
        with open('functions/bounties/channelIDs.pickle', "rb") as f:
            file = pickle.load(f)

        for guild in client.guilds:
            if guild.id == file["guild_id"]:
                # put message in #register channel if there is none
                if "register_channel" in file:
                    if "register_channel_message_id" not in file:
                        channel = discord.utils.get(guild.channels, id=file["register_channel"])
                        await channel.purge(limit=100)

                        # send register msg and save the id
                        msg = await channel.send(embed=embed_message(
                            f'Registration',
                            f'Please react if you want to register to the bounty program'
                        ))
                        await msg.add_reaction("✅")
                        await msg.add_reaction("❎")
                        saveAsGlobalVar("register_channel_message_id", msg.id)

                if "leaderboard_channel" in file:
                    if "leaderboard_channel_message_id" not in file:
                        channel = discord.utils.get(guild.channels, id=file["leaderboard_channel"])
                        await channel.purge(limit=100)

                        # send leaderboard msg
                        await updateLeaderboard(client)

                # if "bounties_channel" in file:
                #     channel = discord.utils.get(guild.channels, id=file["bounties_channel"])
                #     await channel.send("bounties_channel")
                #

                # if "tournament_channel" in file:
                #     channel = discord.utils.get(guild.channels, id=file["tournament_channel"])
                #     await channel.send("tournament_channel")

async def registrationMessageReactions(user, emoji, register_channel, register_channel_message_id):
    message = await register_channel.fetch_message(register_channel_message_id)

    if emoji.name == "✅":
        await message.remove_reaction("✅", user)
        # todo: add to database
        await user.send("you signed up")
    elif emoji.name == "❎":
        await message.remove_reaction("❎", user)
        # todo: remove from database
        await user.send("you're no longer signed up")



