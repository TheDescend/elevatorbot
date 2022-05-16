import asyncio
import dataclasses
from typing import Optional

from naff import ActionRow, Button, ButtonStyles, Message
from naff.api.events import Component

from ElevatorBot.discordEvents.base import ElevatorComponentContext, ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message


@dataclasses.dataclass()
class Calculator:
    ctx: ElevatorInteractionContext

    message: Optional[Message] = None
    buttons: list[ActionRow] = dataclasses.field(init=False)

    def __post_init__(self):
        self.buttons = [
            ActionRow(
                Button(
                    custom_id="c",
                    style=ButtonStyles.RED,
                    label="C",
                ),
                Button(
                    custom_id="(",
                    style=ButtonStyles.GREEN,
                    label="(",
                ),
                Button(
                    custom_id=")",
                    style=ButtonStyles.GREEN,
                    label=")",
                ),
                Button(
                    custom_id="/",
                    style=ButtonStyles.GREEN,
                    label="/",
                ),
            ),
            ActionRow(
                Button(
                    custom_id="7",
                    style=ButtonStyles.BLUE,
                    label="7",
                ),
                Button(
                    custom_id="8",
                    style=ButtonStyles.BLUE,
                    label="8",
                ),
                Button(
                    custom_id="9",
                    style=ButtonStyles.BLUE,
                    label="9",
                ),
                Button(
                    custom_id="*",
                    style=ButtonStyles.GREEN,
                    label="*",
                ),
            ),
            ActionRow(
                Button(
                    custom_id="4",
                    style=ButtonStyles.BLUE,
                    label="4",
                ),
                Button(
                    custom_id="5",
                    style=ButtonStyles.BLUE,
                    label="5",
                ),
                Button(
                    custom_id="6",
                    style=ButtonStyles.BLUE,
                    label="6",
                ),
                Button(
                    custom_id="-",
                    style=ButtonStyles.GREEN,
                    label="-",
                ),
            ),
            ActionRow(
                Button(
                    custom_id="1",
                    style=ButtonStyles.BLUE,
                    label="1",
                ),
                Button(
                    custom_id="2",
                    style=ButtonStyles.BLUE,
                    label="2",
                ),
                Button(
                    custom_id="3",
                    style=ButtonStyles.BLUE,
                    label="3",
                ),
                Button(
                    custom_id="+",
                    style=ButtonStyles.GREEN,
                    label="+",
                ),
            ),
            ActionRow(
                Button(
                    custom_id="(-)",
                    style=ButtonStyles.BLUE,
                    label="(-)",
                ),
                Button(
                    custom_id="0",
                    style=ButtonStyles.BLUE,
                    label="0",
                ),
                Button(
                    custom_id=".",
                    style=ButtonStyles.BLUE,
                    label=".",
                ),
                Button(
                    custom_id="=",
                    style=ButtonStyles.GREEN,
                    label="=",
                ),
            ),
        ]

    # set all buttons to be disabled
    def disable_buttons(self):
        for row in self.buttons:
            for button in row.components:
                button.disabled = True

    async def send_message(
        self,
        text: str = "Please Input Your Equation",
        timeout: bool = False,
        button_ctx: Optional[ElevatorComponentContext] = None,
    ):
        if not self.message:
            embed = embed_message("Calculator", f"```{text}```", member=self.ctx.author)
            self.message = await self.ctx.send(components=self.buttons, embeds=embed)
        else:
            embed = self.message.embeds[0]

            # check if user pressed =
            if "=" in text:
                try:
                    embed.description = f"```{eval(embed.description[3:-3])}```"
                except Exception as e:
                    embed.description = "```Error: Please Try again```"

            # check if user pressed c
            elif "c" in text:
                if not ("Error" in embed.description or "Please" in embed.description):
                    text = ""
                    already_deleted = False
                    for letter in reversed(embed.description):
                        if letter == "`":
                            text = f"{letter}{text}"
                        elif letter == " ":
                            if already_deleted:
                                text = f"{letter}{text}"
                        else:
                            if already_deleted:
                                text = f"{letter}{text}"
                            already_deleted = True
                    embed.description = text if text != "``````" else "```Please Input Your Equation```"

            else:
                if "Error" in embed.description or "Please" in embed.description:
                    embed.description = "``````"

                # special behaviour for * and /
                if "*" in text:
                    if embed.description[-1] == "*":
                        text = text[1]
                elif "/" in text:
                    if embed.description[-1] == "/":
                        text = text[1]

                embed.description = f"```{embed.description[3:-3]}{text}```"

            if timeout:
                embed = embed_message(
                    "Calculator", embed.description, "This calculator is now disabled", member=self.ctx.author
                )
                self.disable_buttons()

            if button_ctx:
                await button_ctx.edit_origin(components=self.buttons, embeds=embed)
            else:
                await self.message.edit(components=self.buttons, embeds=embed)

    # checks that the button press author is the same as the message command invoker and that the message matches
    def check_author_and_message(self, component: Component):
        return (component.context.author == self.ctx.author) and (self.message == component.context.message)

    # wait for button press look
    async def wait_for_button_press(self):
        # wait 60s for button press
        try:
            component: Component = await self.ctx.bot.wait_for_component(
                components=self.buttons,
                timeout=60,
                check=self.check_author_and_message,
            )
        except asyncio.TimeoutError:
            # give timeout message and disable all buttons
            await self.send_message(timeout=True)
            return
        else:
            button_ctx: ElevatorComponentContext = component.context  # noqa
            text = button_ctx.custom_id

            if text not in [
                "0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "(-)",
                ".",
            ]:
                text = f" {text} "

            if text == "(-)":
                text = "-"

            # send new message
            await self.send_message(text=text, button_ctx=button_ctx)

            # wait for new message
            await self.wait_for_button_press()

    # main function
    async def start(self):
        await self.send_message()
        await self.wait_for_button_press()
