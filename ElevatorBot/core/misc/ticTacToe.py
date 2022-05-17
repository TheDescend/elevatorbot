import asyncio
import dataclasses
import random
from typing import Optional

from anyio import to_thread
from naff import ActionRow, Button, ButtonStyles, Member, Message
from naff.api.events import Component

from ElevatorBot.discordEvents.customInteractions import ElevatorComponentContext, ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message


@dataclasses.dataclass()
class TicTacToeGame:
    ctx: ElevatorInteractionContext

    # if versus is off
    easy_mode: bool = False

    # if versus is on
    versus: bool = False
    player1: Optional[Member] = None
    player2: Optional[Member] = None
    player_turn: Optional[Member] = None

    message: Optional[Message] = None
    current_state: list = dataclasses.field(init=False)
    buttons: list[ActionRow] = dataclasses.field(init=False)

    player_symbol: str = "X"
    ai_symbol: str = "O"

    def __post_init__(self):
        self.current_state = [["", "", ""], ["", "", ""], ["", "", ""]]

        self.buttons = [
            ActionRow(
                *[
                    Button(
                        custom_id=str(i),
                        style=ButtonStyles.GREY,
                        label="⁣",
                    )
                    for i in range(1, 4)
                ]
            ),
            ActionRow(
                *[
                    Button(
                        custom_id=str(i),
                        style=ButtonStyles.GREY,
                        label="⁣",
                    )
                    for i in range(4, 7)
                ]
            ),
            ActionRow(
                *[
                    Button(
                        custom_id=str(i),
                        style=ButtonStyles.GREY,
                        label="⁣",
                    )
                    for i in range(7, 10)
                ]
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
        # set best score really low or high, depending on who plays
        if is_maximizing:
            best = [-1, -1, -1000]
        else:
            best = [-1, -1, 1000]

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

            # if they are the same, do some randomisation
            if score[2] == best[2]:
                best = random.choice([best, score])

            if is_maximizing:
                if score[2] > best[2]:
                    best = score
            else:
                if score[2] < best[2]:
                    best = score

        return best

    # checks that the button press author is the same as the message command invoker and that the message matches
    def check_author_and_message(self, component: Component):
        # versus mode
        if self.versus:
            check = self.message.id == component.context.message.id
            if self.player_turn:
                check = check and (component.context.author == self.player_turn)
            elif self.player1:
                check = check and (component.context.author != self.player1)

        # ai mode
        else:
            check = (component.context.author == self.ctx.author) and (self.message.id == component.context.message.id)

        return check

    # play the move and change the board
    async def make_move(
        self, x: int, y: int, symbol: str, button_ctx: Optional[ElevatorComponentContext] = None
    ) -> bool:
        if self.is_valid(x, y):
            self.current_state[x][y] = symbol
            self.buttons[x].components[y].style = (
                ButtonStyles.GREEN if symbol == self.player_symbol else ButtonStyles.RED
            )
            self.buttons[x].components[y].label = symbol

            # either enable or disable the buttons, depending on who plays next
            kwargs = {
                "disable_buttons": (symbol == self.player_symbol) and not self.versus,
                "enable_buttons": (symbol == self.ai_symbol) and not self.versus,
            }
            await self.send_message(button_ctx=button_ctx, **kwargs)
            return True
        else:
            return False

    # Makes the AI move with the minimax implementation
    async def ai_turn(self):
        # check if over
        has_ended = self.is_end()
        if has_ended:
            await self.send_message(winner=has_ended, disable_buttons=True)
            return

        if self.easy_mode:
            empty_cell = random.choice(self.get_empty())
            x, y = empty_cell[0], empty_cell[1]
        else:
            # run the minimax in a thread since it is a lot of calculation
            best_move = await to_thread.run_sync(self.minimax, self.current_state, True)
            x, y = best_move[0], best_move[1]

        await self.make_move(x, y, self.ai_symbol)

        # wait for human input
        await self.human_turn()

    # Waits for a user input and makes the move
    async def human_turn(self):
        # check if over
        has_ended = self.is_end()
        if has_ended:
            await self.send_message(winner=has_ended, disable_buttons=True)
            return

        # wait 60s for button press
        try:
            component: Component = await self.ctx.bot.wait_for_component(
                components=self.buttons,
                timeout=60,
                check=self.check_author_and_message,
            )
        except asyncio.TimeoutError:
            # give timeout message and disable all buttons
            await self.send_message(timeout=True, disable_buttons=True)
            return
        else:
            button_ctx: ElevatorComponentContext = component.context  # noqa

            # make sure the players are set
            if self.versus:
                if not self.player1:
                    self.player1 = button_ctx.author
                elif not self.player2:
                    self.player2 = button_ctx.author

            # possible player moves (button ids) and their corresponding x, y values
            moves = {
                "1": [0, 0],
                "2": [0, 1],
                "3": [0, 2],
                "4": [1, 0],
                "5": [1, 1],
                "6": [1, 2],
                "7": [2, 0],
                "8": [2, 1],
                "9": [2, 2],
            }

            # get the move from the button id
            player_move = moves[button_ctx.custom_id]

            # set the symbol
            symbol = self.ai_symbol if self.versus and self.player2 == button_ctx.author else self.player_symbol

            # make the move
            valid = await self.make_move(player_move[0], player_move[1], symbol, button_ctx)
            assert valid, "Move was not valid for some reason"

            # make the other human turn
            if self.versus:
                # set the next turn to belong to the other player
                self.player_turn = self.player2 if button_ctx.author == self.player1 else self.player1

                # wait for other players move
                await self.human_turn()

            # make the ai turn
            else:
                await self.ai_turn()

    # Checks if the game has ended and returns the winner in each case
    def is_end(self) -> bool | str:
        # Vertical win
        for i in range(0, 3):
            if (
                self.current_state[0][i] != ""
                and self.current_state[0][i] == self.current_state[1][i]
                and self.current_state[1][i] == self.current_state[2][i]
            ):
                return self.current_state[0][i]

        # Horizontal win
        for i in range(0, 3):
            if self.current_state[i] == [
                self.player_symbol,
                self.player_symbol,
                self.player_symbol,
            ]:
                return self.player_symbol
            elif self.current_state[i] == [
                self.ai_symbol,
                self.ai_symbol,
                self.ai_symbol,
            ]:
                return self.ai_symbol

        # Main diagonal win
        if (
            self.current_state[0][0] != ""
            and self.current_state[0][0] == self.current_state[1][1]
            and self.current_state[0][0] == self.current_state[2][2]
        ):
            return self.current_state[0][0]

        # Second diagonal win
        if (
            self.current_state[0][2] != ""
            and self.current_state[0][2] == self.current_state[1][1]
            and self.current_state[0][2] == self.current_state[2][0]
        ):
            return self.current_state[0][2]

        # Is whole board full?
        for i in range(0, 3):
            for j in range(0, 3):
                # There's an empty field, we continue the game
                if self.current_state[i][j] == "":
                    return False

        # It's a tie!
        return "T"

    # set all buttons to be disabled
    def disable_buttons(self):
        for row in self.buttons:
            for button in row.components:
                button.disabled = True

    # set grey buttons to be enabled
    def enable_buttons(self):
        for row in self.buttons:
            for button in row.components:
                if button.style == ButtonStyles.GREY:
                    button.disabled = False

    # update the user message
    async def send_message(
        self,
        winner: Optional[str] = None,
        disable_buttons: bool = False,
        enable_buttons: bool = False,
        timeout: bool = False,
        button_ctx: Optional[ElevatorComponentContext] = None,
    ):
        if disable_buttons:
            self.disable_buttons()

        if enable_buttons:
            self.enable_buttons()

        if not self.message:
            embed = embed_message(
                f"{self.ctx.author.display_name}'s TicTacToe Game",
                footer=f"""You are green{f" - Easy Mode: On" if self.easy_mode else ""}"""
                if not self.versus
                else "First user to press a button plays green, second plays red",
            )
            self.message = await self.ctx.send(components=self.buttons, embeds=embed)
        else:
            # get the embed
            embed = self.message.embeds[0]

            # check if message reason is a timeout
            if timeout:
                embed.description = (
                    "**You Lost:** You took to long to play"
                    if not self.versus
                    else f"""{"**Red Wins:** Green took to long to play" if self.player_turn == self.player1 else "**Green Wins:** Red took to long to play"}"""
                )

            # check if there is a winner
            elif winner:
                if winner == self.player_symbol:
                    text = "**You Won:** Try the hard mode next time 🙃" if not self.versus else "**Green Wins**"
                elif winner == self.ai_symbol:
                    banter = [
                        "Imagine losing in Tic Tac Toe",
                        "Get on my level human",
                        "Tough game... NOT",
                        "This was so easy, I nearly fell asleep",
                        "Next time you got it... Maybe",
                        "Believe in yourself, somebody has too",
                        "Do I need to explain the rules to you?",
                        "You sure you played this game before",
                        "Hopefully that was not your A game",
                        "You know you can win nitro here right?",
                        "<@238388130581839872> would have won",
                    ]
                    text = f"**You Lost:** {random.choice(banter)}" if not self.versus else "**Red Wins**"
                else:
                    text = "**Tie:** Better luck next time"

                embed.description = text

            # to satisfy the button context
            if button_ctx:
                await button_ctx.edit_origin(components=self.buttons, embeds=embed)
            else:
                await self.message.edit(components=self.buttons, embeds=embed)

    # main function
    async def play_game(self):
        # send the first message
        await self.send_message()

        # start with human turn
        await self.human_turn()
