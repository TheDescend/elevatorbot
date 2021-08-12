import asyncio
import json
import random
import time

from functions.destinyPlayer import DestinyPlayer
from functions.formating import embed_message
from functions.miscFunctions import has_elevated_permissions
from networking.network import get_json_from_url


async def startTournamentEvents(
    client,
    tourn_msg,
    tourn_channel,
    tourn_participants
):
    await edit_tourn_message(tourn_msg, tourn_participants)

    # start the tourn
    tourn = Tournament(tourn_participants, tourn_msg)
    return await tourn.playTournament(client, tourn_channel)


async def edit_tourn_message(
    msg,
    tourn_participants,
    eliminated=None
):
    if eliminated is None:
        eliminated = []

    participants_cleaned = []
    for participant in tourn_participants:
        if participant in eliminated:
            participants_cleaned.append(f"~~{participant.display_name}~~")
        else:
            participants_cleaned.append(f"{participant.display_name}")

    text = f"""
<:desc_title_left_b:768906489309822987><:desc_title_right_b:768906489729122344> **Ongoing Tournament** <:desc_title_left_b:768906489309822987><:desc_title_mid_b:768906489103384657><:desc_title_mid_b:768906489103384657><:desc_title_right_b:768906489729122344>
⁣
__Participants:__
{", ".join(participants_cleaned)}
⁣"""

    await msg.edit(content=text, embed=None)


class Tournament:


    def __init__(
        self,
        players,
        tourn_message
    ):
        self.player_id_translation = {}
        self.players = players
        self.tourn_message = tourn_message
        self.eliminated = []


    async def playTournament(
        self,
        client,
        tourn_channel
    ):
        # takes players[discordID1, discordID2, ...] and returns bracket = [], player_id_translation = {}
        def getBracket(
            players
        ):
            # makes the bracket
            def divide(
                arr,
                depth,
                m
            ):
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
        async def playBracket(
            client,
            tourn_channel,
            bracket
        ):
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
                    bracket[0], bracket[1] = await asyncio.gather(
                        *[playBracket(client, tourn_channel, bracket[0]), playBracket(client, tourn_channel, bracket[1])]
                    )
                elif bracket[0] in to_play:
                    bracket[0] = await playBracket(client, tourn_channel, bracket[0])
                elif bracket[1] in to_play:
                    bracket[1] = await playBracket(client, tourn_channel, bracket[1])

            won = await playGame(client, tourn_channel, bracket[0], bracket[1])

            return won


        # waits for the end of the game and then returns the winner
        async def playGame(
            client,
            tourn_channel,
            player1,
            player2
        ):
            # this pretty much needs to look at player1's match history every 10s and return the winner whenever the game with just both players ends up the in the api

            print(f"Playing game: {player1} vs {player2}")

            user1 = self.player_id_translation[player1]
            user2 = self.player_id_translation[player2]

            destiny_player1 = await DestinyPlayer.from_discord_id(user1.id)
            destiny_player2 = await DestinyPlayer.from_discord_id(user2.id)

            which_user_is_which_emoji = {
                755044614850740304: destiny_player1.destiny_id,
                755044614733561916: destiny_player2.destiny_id,
            }

            characters1 = await destiny_player1.get_character_info()

            timeout = time.time() + 60 * 60  # 60 minutes from now

            # send message in chat with reactions for both players. If an admin / dev reacts to them, he can overwrite the auto detection, if it breaks for some reason
            msg = await tourn_channel.send(
                embed=embed_message(
                    f"(1) - **{user1.display_name}** vs ** {user2.display_name}** - (2)",
                    f"To play, create a private crucible game where __only__ you two take part in and **finish the game and not leave early**",
                    "If for some reason the auto detect fails, ask an admin / dev to react on the winner"
                )
            )
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
                won = await returnCustomGameWinner(destiny_player1.destiny_id, characters1, destiny_player1.system, destiny_player2.destiny_id)

                # check if there are new reactions, delete them and check if an admin reacted and make that reaction the winner
                # msg object has to be reloaded
                msg = await tourn_channel.fetch_message(msg.id)
                for reaction in msg.reactions:
                    async for user in reaction.users():
                        if not user.bot:
                            if await has_elevated_permissions(user, tourn_channel.guild):
                                print("Detected manual game winner overwrite")
                                for reaction_id in which_user_is_which_emoji:
                                    if reaction.emoji.id == reaction_id:
                                        won = which_user_is_which_emoji[reaction_id]
                            await reaction.remove(user)

                # return winner if found
                if won:
                    if won == destiny_player1.destiny_id:
                        won = player1
                        self.eliminated.append(user2)
                    else:
                        won = player2
                        self.eliminated.append(user1)

                    await msg.delete()

                    # edit participants msg
                    await edit_tourn_message(self.tourn_message, self.players, eliminated=self.eliminated)

                    return won

                # wait a bit
                await asyncio.sleep(10)


        # randomize the bracket
        players = random.sample(self.players, len(self.players))
        # generate the bracket
        bracket, self.player_id_translation = getBracket(players)

        # play the bracket
        winner = await playBracket(client, tourn_channel, bracket)
        winner = self.player_id_translation[winner]

        return winner


async def returnCustomGameWinner(
    destinyID1,
    charIDs1,
    membershipType1,
    destinyID2
):
    for char in charIDs1:
        staturl = f"https://www.bungie.net/Platform/Destiny2/{membershipType1}/Account/{destinyID1}/Character/{char}/Stats/Activities/?mode=0&count=1&page=0"
        rep = await get_json_from_url(staturl)
        if rep:
            rep.content = json.loads(json.dumps(rep.content))
            # if it's not a private game
            if not rep.content["Response"]["activities"][0]["activityDetails"]["isPrivate"]:
                return None

            # if it's not completed
            if not int(rep.content["Response"]["activities"][0]["values"]["completed"]["basic"]["value"]) == 1:
                return None

            ID = rep.content["Response"]["activities"][0]["activityDetails"]["instanceId"]
            staturl = f"https://stats.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/{ID}/"
            rep2 = await get_json_from_url(staturl)
            if rep2:
                rep2.content = json.loads(json.dumps(rep2.content))

                # if more / less than 2 players
                if len(rep2.content["Response"]["entries"]) != 2:
                    return None

                found1, found2 = False, False
                for player in rep2.content["Response"]["entries"]:
                    if int(player["player"]["destinyUserInfo"]["membershipId"]) == int(destinyID1):
                        found1 = True
                    elif int(player["player"]["destinyUserInfo"]["membershipId"]) == int(destinyID2):
                        found2 = True

                # players need to be the once specified
                if found1 and found2:
                    if rep.content["Response"]["activities"][0]["values"]["standing"]["basic"]["displayValue"] == "Victory":
                        return destinyID1
                    else:
                        return destinyID2
    return None
