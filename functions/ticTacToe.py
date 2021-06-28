import asyncio
import dataclasses
from typing import Union

from discord_slash import SlashContext, ComponentContext
from discord_slash.model import SlashMessage, ButtonStyle
from discord_slash.utils import manage_components

from functions.formating import embed_message





@dataclasses.dataclass()
class TicTacToeGame:
    ctx: SlashContext

    message: SlashMessage = None
    current_state: list = dataclasses.field(init=False)
    buttons: list[list] = dataclasses.field(init=False)

    player_symbol = "X"
    ai_symbol = "O"

    def __post_init__(self):
        self.current_state = [['', '', ''],
                              ['', '', ''],
                              ['', '', '']]

        self.buttons = [
            manage_components.create_actionrow(*[
                manage_components.create_button(
                    custom_id=i,
                    style=ButtonStyle.grey,
                    label="⁣",
                ) for i in range(1, 4)]
            ),
            manage_components.create_actionrow(*[
                manage_components.create_button(
                    custom_id=i,
                    style=ButtonStyle.grey,
                    label="⁣",
                ) for i in range(4, 7)]
            ),
            manage_components.create_actionrow(*[
                manage_components.create_button(
                    custom_id=i,
                    style=ButtonStyle.grey,
                    label="⁣",
                ) for i in range(7, 10)]
            ),
        ]

    # Determines if the made move is a legal move
    def is_valid(self, x: int, y: int) -> bool:
        if [x, y] in self.get_empty():
            return True
        else:
            return False

    # Gets the empty cells
    def get_empty(self) -> list:
        empty_cells = []

        for x, row in enumerate(self.current_state):
            for y, cell in enumerate(row):
                if cell == "":
                    empty_cells.append([x, y])

        return empty_cells

    # looks for the best move and returns a list with [the best row, best col, best score]
    def minimax(self, state: list[list], is_maximizing: bool) -> list:
        # set best score really low
        best = [-1, -1, -10]

        # get the winner
        has_ended = self.is_end()
        if has_ended:
            # player won
            if has_ended == self.player_symbol:
                score = -1
            # ai won
            elif has_ended == self.ai_symbol:
                score = 1
            # tie
            else:
                score = 0

            return [-1, -1, score]

        for empty_cell in self.get_empty():
            x, y = empty_cell[0], empty_cell[1]
            state[x][y] = self.ai_symbol if is_maximizing else self.player_symbol
            score = self.minimax(state, is_maximizing=not is_maximizing)
            state[x][y] = ""
            score[0], score[1] = x, y

            if is_maximizing:
                if score[2] > best[2]:
                    best = score  # max value
            else:
                if score[2] < best[2]:
                    best = score  # min value

        return best

    # play the move and change the board
    def make_move(self, x: int, y: int, symbol: str) -> bool:
        if self.is_valid(x, y):
            self.current_state[x][y] = symbol
            return True
        else:
            return False

    # Makes the AI move with the minimax implementation
    def ai_turn(self):
        # check if over
        has_ended = self.is_end()
        if has_ended:
            self._send_message(winner=has_ended)
            return

        best_move = self.minimax(self.current_state, is_maximizing=True)
        x, y = best_move[0], best_move[1]

        self.make_move(x, y, self.ai_symbol)

    # Waits for a user input and makes the move
    async def human_turn(self):
        # check if over
        has_ended = self.is_end()
        if has_ended:
            await self._send_message(winner=has_ended)
            return

        # wait 60s for button press
        try:
            button_ctx: ComponentContext = await manage_components.wait_for_component(self.ctx.bot, components=self.buttons, timeout=60)
        except asyncio.TimeoutError:
            embed = self.message.embeds[0]
            embed.description = "**You Lost:** You took to long to play"
            await self.message.edit(embed=embed)
            return
        else:
            await button_ctx.edit_origin()
            activity = button_ctx.component["label"]
            max_joined_members = 3


    # Checks if the game has ended and returns the winner in each case
    def is_end(self) -> Union[bool, str]:
        # Vertical win
        for i in range(0, 3):
            if (self.current_state[0][i] != '' and
                    self.current_state[0][i] == self.current_state[1][i] and
                    self.current_state[1][i] == self.current_state[2][i]):
                return self.current_state[0][i]

        # Horizontal win
        for i in range(0, 3):
            if self.current_state[i] == [self.player_symbol, self.player_symbol, self.player_symbol]:
                return self.player_symbol
            elif self.current_state[i] == [self.ai_symbol, self.ai_symbol, self.ai_symbol]:
                return self.ai_symbol

        # Main diagonal win
        if (self.current_state[0][0] != '' and
                self.current_state[0][0] == self.current_state[1][1] and
                self.current_state[0][0] == self.current_state[2][2]):
            return self.current_state[0][0]

        # Second diagonal win
        if (self.current_state[0][2] != '' and
                self.current_state[0][2] == self.current_state[1][1] and
                self.current_state[0][2] == self.current_state[2][0]):
            return self.current_state[0][2]

        # Is whole board full?
        for i in range(0, 3):
            for j in range(0, 3):
                # There's an empty field, we continue the game
                if self.current_state[i][j] == '':
                    return False

        # It's a tie!
        return 'T'

    # update the user message
    async def _send_message(self, winner: str = None):
        if not self.message:
            embed = embed_message(
                f"{self.ctx.author.display_name}'s TicTacToe Game"
            )
            self.message = await self.ctx.send(components=self.buttons, embed=embed)
        else:
            await self.message.edit(components=self.buttons)

    # main function
    async def play_game(self):

        await self._send_message()



