from functions.bounties.bountiesBackend import returnCustomGameWinner
from functions.database     import lookupDestinyID

import asyncio

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
        async def playGame(player1, player2):
            # this pretty much needs to look at player1's match history every 10s and return the winner whenever the game with just both players ends up the in the api

            destinyID1 = lookupDestinyID(self.player_id_translation[player1])
            destinyID2 = lookupDestinyID(self.player_id_translation[player2])

            while True:
                won = returnCustomGameWinner(destinyID1, destinyID2)
                if won:
                    return won
                asyncio.sleep(10)


            # won = input(f"who won, {player1} or {player2}")
            #
            # if int(won) == player1:
            #     return player1
            # elif int(won) == player2:
            #     return player2
            # else:
            #     return False

        # players = ["ich", "du", "er", "sie", "wir"]
        bracket, self.player_id_translation = getBracket(players)

        loop = asyncio.get_event_loop()
        winner = loop.run_until_complete(playBracket(bracket))

        print(winner)





