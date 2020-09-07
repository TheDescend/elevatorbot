from functions.bounties.bountiesBackend import returnCustomGameWinner
from functions.database import lookupDestinyID
from functions.network import getJSONfromURL
from functions.formating import embed_message

import asyncio
import time
import discord

class Tournament():
    def __init__(self):
        self.player_id_translation = {}

    def playTournament(self, players):
        # takes players[discordID, ...] and returns bracket = [], player_id_translation = {}
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
        async def playBracket(bracket):
            print(bracket)
            if isinstance(bracket[0], list):
                bracket[0] = playBracket(bracket[0])
            if isinstance(bracket[1], list):
                bracket[1] = playBracket(bracket[1])

            won = await playGame(bracket[0], bracket[1])

            return won

        # waits for the end of the game and then returns the winner
        async def playGame(client, tourn_channel, player1, player2):
            # this pretty much needs to look at player1's match history every 10s and return the winner whenever the game with just both players ends up the in the api

            admin = discord.utils.get(tourn_channel.guild.roles, name='Admin')
            dev = discord.utils.get(tourn_channel.guild.roles, name='Developer')

            discordID1 = self.player_id_translation[player1]
            discordID2 = self.player_id_translation[player2]

            user1 = client.get_user(discordID1)
            user2 = client.get_user(discordID2)

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
        bracket, self.player_id_translation = getBracket(players)

        loop = asyncio.get_event_loop()
        winner = loop.run_until_complete(playBracket(bracket))

        print(winner)





