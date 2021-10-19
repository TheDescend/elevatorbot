import asyncio
import dataclasses

from dis_snek.models import ActionRow
from dis_snek.models import Button
from dis_snek.models import ButtonStyles
from dis_snek.models import ComponentContext
from dis_snek.models import InteractionContext
from dis_snek.models import Message

from ElevatorBot.misc.formating import embed_message


@dataclasses.dataclass()
class Calculator:
    ctx: InteractionContext

    message: Message = None
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
            for button in row["components"]:
                button_update = {"disabled": True}
                button._update(button_update)

    async def send_message(
        self,
        text: str = "Please Input Your Equation",
        timeout: bool = False,
        button_ctx: ComponentContext = None,
    ):
        if not self.message:
            embed = embed_message(f"{self.ctx.author.display_name}'s Calculator", f"```{text}```")
            self.message = await self.ctx.send(components=self.buttons, embeds=embed)
        else:
            embed = self.message.embeds[0]

            # check if user pressed =
            if "=" in text:
                try:
                    embed.description = f"```{eval(embed.description[3:-3])}```"
                except:
                    embed.description = f"```Error: Please Try again```"
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
                embed.description = f"```{embed.description[3:-3]}{text}```"

            if timeout:
                embed = embed_message(
                    f"{self.ctx.author.display_name}'s Calculator",
                    embed.description,
                    "This calculator is now disabled",
                )
                self.disable_buttons()

            if button_ctx:
                await button_ctx.edit_origin(components=self.buttons, embeds=embed)
            else:
                await self.message.edit(components=self.buttons, embeds=embed)

    # checks that the button press author is the same as the message command invoker and that the message matches
    def check_author_and_message(self, ctx: ComponentContext):
        return (ctx.author == self.ctx.author) and (self.ctx.message.id == ctx.origin_message.id)

    # wait for button press look
    async def wait_for_button_press(self):
        # wait 60s for button press
        try:
            # todo
            button_ctx: ComponentContext = await wait_for_component(
                self.ctx.bot,
                components=self.buttons,
                timeout=60,
                check=self.check_author_and_message,
            )
        except asyncio.TimeoutError:
            # give timeout message and disable all buttons
            await self.send_message(timeout=True)
            return
        else:
            text = button_ctx.component_id

            if text == "(-)":
                text = "-"

            if button_ctx.component_id not in [
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

            # send new message
            await self.send_message(text=text, button_ctx=button_ctx)

            # wait for new message
            await self.wait_for_button_press()

    # main function
    async def start(self):
        await self.send_message()
        await self.wait_for_button_press()
