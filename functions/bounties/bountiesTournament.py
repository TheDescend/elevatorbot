from functions.bounties.bountiesBackend import returnCustomGameWinner, getGlobalVar, saveAsGlobalVar, addPoints
from functions.database import lookupDestinyID, getBountyUserList
from functions.network import getJSONfromURL
from functions.formating import embed_message

import asyncio
import time
import discord
import random
import pickle


async def startTournamentEvents(client):
    file = getGlobalVar()
    for guild in client.guilds:
            if guild.id == file["guild_id"]:
                # get channel / message
                tourn_channel = discord.utils.get(guild.channels, id=file["tournament_channel"])
                tourn_register_msg = await tourn_channel.fetch_message(file["tournament_channel_message_id"])

                bounty_users = getBountyUserList()

                # get users that registered
                registered_users = []
                registered_users_names = []
                register = client.get_emoji(754946724233216100)
                for reaction in tourn_register_msg.reactions:
                    if reaction.emoji == register:
                        async for user in reaction.users():
                            if user != client.user:
                                if user.id in bounty_users:
                                    registered_users.append(user.id)
                                    registered_users_names.append(user.display_name)
                print(f"Tournament Participants: {registered_users}")

                # clear channel
                await tourn_channel.purge(limit=100)

                # print participants
                await tourn_channel.send(
f""" ** Participants:**
⁣
{", ".join(registered_users_names)}
⁣
"""
                )

                # start and play the tourn
                print("Starting Tournament...")
                tourn = Tournament()
                await tourn.playTournament(client, tourn_channel, registered_users)


# prints the msg that users have to react to register
async def tournamentRegistrationMessage(client):
    file = getGlobalVar()

    for guild in client.guilds:
        if guild.id == file["guild_id"]:
            channel = discord.utils.get(guild.channels, id=file["tournament_channel"])

            # send register msg and save the id
            msg = await channel.send(embed=embed_message(
                f'Registration',
                f'If you want to register to the tournament this week, react with <:elevator_yes:754946724233216100> '
            ))
            register = client.get_emoji(754946724233216100)
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

    async def playTournament(self, client, tourn_channel, players):
        # takes players[discordID1, discordID2, ...] and returns bracket = [], player_id_translation = {}
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
                player_id_translation[players.index(player) + 1] = player

            return bracket, player_id_translation

        # loops through the bracket and plays the games
        async def playBracket(client, tourn_channel, bracket):
            print(f"Bracket: {bracket}")

            # checks if bracket has sub-brackets that need to play first
            to_play = []
            if isinstance(bracket[0], list):
                to_play.append(bracket[0])
            if isinstance(bracket[1], list):
                to_play.append(bracket[1])

            # if there are any sub brackets, play them first
            if to_play:
                if len(to_play) == 2:
                    bracket[0], bracket[1] = await asyncio.gather(*[playBracket(client, tourn_channel, bracket[0]), playBracket(client, tourn_channel, bracket[1])])
                elif bracket[0] in to_play:
                    bracket[0] = await playBracket(client, tourn_channel, bracket[0])
                elif bracket[1] in to_play:
                    bracket[1] = await playBracket(client, tourn_channel, bracket[1])

            won = await playGame(client, tourn_channel, bracket[0], bracket[1])

            return won

        # waits for the end of the game and then returns the winner
        async def playGame(client, tourn_channel, player1, player2):
            # this pretty much needs to look at player1's match history every 10s and return the winner whenever the game with just both players ends up the in the api

            print(f"Playing game: {player1} vs {player2}")

            admin = discord.utils.get(tourn_channel.guild.roles, name='Admin')
            dev = discord.utils.get(tourn_channel.guild.roles, name='Developer')

            discordID1 = self.player_id_translation[player1]
            discordID2 = self.player_id_translation[player2]

            user1 = client.get_user(discordID1)
            user2 = client.get_user(discordID2)

            destinyID1 = lookupDestinyID(discordID1)
            destinyID2 = lookupDestinyID(discordID2)

            which_user_is_which_emoji = {
                569576890512179220: destinyID1,
                569576890470498315: destinyID2,
            }
            destinyID_to_player = {
                destinyID1: player1,
                destinyID2: player2,
            }

            membershipType1 = None
            charIDs1 = []
            for i in [3, 2, 1, 4, 5, 10, 254]:
                characterinfo = await getJSONfromURL(
                    f"https://www.bungie.net/Platform/Destiny2/{i}/Profile/{destinyID1}/?components=100")
                if characterinfo:
                    membershipType1 = i
                    charIDs1 = characterinfo['Response']["profile"]["data"]["characterIds"]

            timeout = time.time() + 60 * 60  # 60 minutes from now

            # send message in chat with reactions for both players. If an admin / dev reacts to them, he can overwrite the auto detection, if it breaks for some reason
            msg = await tourn_channel.send(embed=embed_message(
                f"(1) - **{user1.display_name}** vs ** {user2.display_name}** - (2)",
                f"To play, create a private crucible game where __only__ you two take part in. Set the time limit / rules as you guys want, but make sure to finish the game and not leave early. \n The winner of the game will auto detect a short while after the game is complete. \n⁣\n **Good luck!**",
                "If for some reason the auto detect fails, ask an admin / dev to react on the winner"
            ))
            reaction1 = client.get_emoji(755044614850740304)
            reaction2 = client.get_emoji(755044614733561916)
            await msg.add_reaction(reaction1)
            await msg.add_reaction(reaction2)

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
                won = await returnCustomGameWinner(destinyID1, charIDs1, membershipType1, destinyID2)

                # check if there are new reactions, delete them and check if an admin reacted and make that reaction the winner
                # msg object has to be reloaded
                msg = await tourn_channel.fetch_message(msg.id)
                for reaction in msg.reactions:
                    async for user in reaction.users():
                        if user != client.user:
                            if admin in user.roles or dev in user.roles:
                                print("Detected manual game winner overwrite")
                                for reaction_id in which_user_is_which_emoji:
                                    if reaction.emoji.id == reaction_id:
                                        won = which_user_is_which_emoji[reaction_id]
                            await reaction.remove(user)

                # return winner if found
                if won:
                    await msg.edit(embed=embed_message(
                        f"(1) - **{user1.display_name}** vs ** {user2.display_name}** - (2)",
                        f"**{user1.display_name if destinyID1 == won else user2.display_name} won!**"
                    ))
                    await msg.clear_reactions()

                    if won == destinyID1:
                        won = player1
                    else:
                        won = player2

                    return won

                # wait a bit
                await asyncio.sleep(10)

        # randomize the bracket
        players = random.sample(players, len(players))
        # generate the bracket
        bracket, self.player_id_translation = getBracket(players)

        # play the bracket
        winner = await playBracket(client, tourn_channel, bracket)
        winner = self.player_id_translation[winner]
        winner = client.get_user(winner)

        print(f"Winner: {winner.display_name}")
        await tourn_channel.send(embed=embed_message(
            "We have a winner!",
            f"Congratulations {winner.display_name}"
        ))

        # try and award points
        with open('functions/bounties/currentBounties.pickle', "rb") as f:
            bounties = pickle.load(f)["competition_bounties"]
        for topic in bounties:
            for key, value in bounties[topic].items():
                if "tournament" in value["requirements"]:
                    addPoints(winner.id, value, key, f"points_competition_{topic.lower()}")
                    print("Added points to winner")






