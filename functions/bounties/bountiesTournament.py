from functions.bounties.bountiesBackend import returnCustomGameWinner, getGlobalVar, saveAsGlobalVar
from functions.database import lookupDestinyID
from functions.network import getJSONfromURL
from functions.formating import embed_message

import asyncio
import time
import discord
import random
import os
import concurrent.futures


async def startTournamentEvents(client):
    file = getGlobalVar()
    for guild in client.guilds:
            if guild.id == file["guild_id"]:
                # get channel / message
                tourn_channel = discord.utils.get(guild.channels, id=file["tournament_channel"])
                tourn_register_msg = await tourn_channel.fetch_message(file["tournament_channel_message_id"])

                # get users that registered
                registered_users = []
                register = client.get_emoji(724678414925168680)
                for reaction in tourn_register_msg.reactions:
                    if reaction.emoji == register:
                        reaction_users = await reaction.users().flatten()
                        for user in reaction_users:
                            if user != client.user:
                                registered_users.append(user)
                print(registered_users)

                # clear channel
                await tourn_channel.purge(limit=100)

                # print participants
                await tourn_channel.send(
f""" ** Participants:**
⁣
{", ".join([name.display_name for name in registered_users])}
⁣
"""
                )

                # start and play the tourn
                print("playing tourn")

                # delete old messages and print the default one back
                await tournamentChannelMessage(client)


# prints the msg that users have to react to register
async def tournamentRegistrationMessage(client):
    file = getGlobalVar()

    for guild in client.guilds:
        if guild.id == file["guild_id"]:
            channel = discord.utils.get(guild.channels, id=file["tournament_channel"])

            # send register msg and save the id
            msg = await channel.send(embed=embed_message(
                f'Registration',
                f'If you want to register to the tournament this week, react with <:unbroken:724678414925168680>'
            ))
            register = client.get_emoji(724678414925168680)
            await msg.add_reaction(register)
            saveAsGlobalVar("tournament_channel_message_id", msg.id)


# prints the default message and changes that should a tourn start
async def tournamentChannelMessage(client):
    file = getGlobalVar()

    for guild in client.guilds:
        if guild.id == file["guild_id"]:
            channel = discord.utils.get(guild.channels, id=file["tournament_channel"])

            # clean messages
            await channel.purge(limit=100)

            # displays the default message that sits in the channel while no tourn is running
            await channel.send(
f""" Welcome to the **Tournament Channel**!
⁣
Every so often, the weekly PvP competition bounty will be a clan wide tournament.
When that happens, you can come back to this channel to register for it. 
⁣
When the games start, I will generate a random bracket and assign player to games.
You will then start a custom game with __only__ the two chosen players in it.
Last man standing wins it all!
⁣
⁣
**Rules**: You decide.
**Time**: The tournament will get manually started by an admin, so try to find a good time for everyone.
⁣
⁣
"""
            )


class Tournament():
    def __init__(self):
        self.player_id_translation = {}

    def playTournament(self, players):
        # takes players[discord.user1, discord.user2, ...] and returns bracket = [], player_id_translation = {}
        def getBracket(players):
            # makes the bracket
            def divide(arr, depth, m):
                if len(complements) <= depth:
                    complements.append(2 ** (depth + 2) + 1)
                complement = complements[depth]
                for i in range(2):
                    if complement - arr[i] <= m:
                        arr[i] = [arr[i], complement - arr[i]]
                        divide(arr[i], depth + 1, m)

            m = len(players)
            complements = []
            bracket = [1, 2]
            divide(bracket, 0, m)

            player_id_translation = {}
            for player in players:
                player_id_translation[players.index(player) + 1] = player.id

            return bracket, player_id_translation

        # loops through the bracket and plays the games
        async def playBracket(bracket):
            print(bracket)

            # checks if bracket has sub-brackets that need to play first
            to_play = []
            if isinstance(bracket[0], list):
                bracket[0] = playBracket(bracket[0])
            if isinstance(bracket[1], list):
                bracket[1] = playBracket(bracket[1])

            # if there are any sub brackets, play them first
            if to_play:
                with concurrent.futures.ThreadPoolExecutor(os.cpu_count() * 2) as pool:
                    futurelist = [pool.submit(playBracket, new_bracket) for new_bracket in to_play]

                    i = 0
                    for future in concurrent.futures.as_completed(futurelist):
                        bracket[i] = future.result()
                        i += 1

            won = await playGame(bracket[0], bracket[1])

            return won

        # waits for the end of the game and then returns the winner
        async def playGame(client, tourn_channel, player1, player2):
            # this pretty much needs to look at player1's match history every 10s and return the winner whenever the game with just both players ends up the in the api

            admin = discord.utils.get(tourn_channel.guild.roles, name='Admin')
            dev = discord.utils.get(tourn_channel.guild.roles, name='Developer')

            user1 = self.player_id_translation[player1]
            user2 = self.player_id_translation[player2]

            discordID1 = user1.id
            discordID2 = user2.id

            destinyID1 = lookupDestinyID(discordID1)
            destinyID2 = lookupDestinyID(discordID2)

            membershipType1 = None
            charIDs1 = []
            for i in [3, 2, 1, 4, 5, 10, 254]:
                characterinfo = getJSONfromURL(
                    f"https://www.bungie.net/Platform/Destiny2/{i}/Profile/{destinyID1}/?components=100")
                if characterinfo:
                    membershipType1 = i
                    charIDs1 = characterinfo['Response']["profile"]["data"]["characterIds"]

            timeout = time.time() + 60 * 60  # 60 minutes from now

            # send message in chat with reactions for both players. If an admin / dev reacts to them, he can overwrite the auto detection, if it breaks for some reason
            msg = await tourn_channel.send(embed_message(
                "Game",
                f"**1 - {user1.display_name}** VS ** {user2.display_name} - 2 \n⁣\n To play, create a private crucible game where __only__ you two take part in. Set the time limit as you guys want, but make sure to finish the game and not leave early. \n The winner of the game will auto detect a short while after the game is complete. \n⁣\n **Good luck!**",
                "If for some reason the auto detect fails, ask an admin / dev to react on the winner"
            ))
            await msg.add_reaction("\U00000031")
            await msg.add_reaction("\U00000032")

            mention1 = await tourn_channel.send(user1.mention)
            mention2 = await tourn_channel.send(user2.mention)
            await mention1.delete()
            await mention2.delete()

            while True:
                # timeout
                if time.time() > timeout:
                    print("Waited too long for result")
                    return False

                # look up winner of game
                won = returnCustomGameWinner(destinyID1, charIDs1, membershipType1, destinyID2)

                # check if there are new reactions, delete them and check if an admin reacted and make that reaction the winner
                for reaction in msg.reactions:
                    reaction_users = await reaction.users().flatten()
                    for user in reaction_users:
                        if user != client.user:
                            if admin in user.roles or dev  in user.roles:
                                if reaction.emoji == "\U00000031":
                                    won = player1
                                elif reaction.emoji == "\U00000032":
                                    won = player2
                            await reaction.remove(user)

                # return winner if found
                if won:
                    await msg.edit(embed_message(
                        "Game",
                        f"**1 - {user1.display_name}** VS ** {user2.display_name} - 2** \n⁣\n **{user1.display_name if destinyID1 == won else user2.display_name} won!**"
                    ))
                    await msg.clear_reactions()

                    if won == destinyID1:
                        won = player1
                    else:
                        won = player2

                    return won

                # wait a bit
                await asyncio.sleep(10)


        # players = ["ich", "du", "er", "sie", "wir"]
        bracket, self.player_id_translation = getBracket(random.sample(players, len(players)))

        loop = asyncio.get_event_loop()
        winner = loop.run_until_complete(playBracket(bracket))

        print(winner)





