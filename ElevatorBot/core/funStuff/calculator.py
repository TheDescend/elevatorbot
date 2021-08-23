import asyncio
import dataclasses

from discord_slash import SlashContext, ComponentContext
from discord_slash.model import SlashMessage, ButtonStyle
from discord_slash.utils import manage_components

from ElevatorBot.misc.formating import embed_message


@dataclasses.dataclass()
class Calculator:
    ctx: SlashContext

    message: SlashMessage = None
    buttons: list[dict] = dataclasses.field(init=False)

    def __post_init__(self):
        self.buttons = [
            manage_components.create_actionrow(
                manage_components.create_button(
                    custom_id="c",
                    style=ButtonStyle.red,
                    label="C",
                ),
                manage_components.create_button(
                    custom_id="(",
                    style=ButtonStyle.green,
                    label="(",
                ),
                manage_components.create_button(
                    custom_id=")",
                    style=ButtonStyle.green,
                    label=")",
                ),
                manage_components.create_button(
                    custom_id="/",
                    style=ButtonStyle.green,
                    label="/",
                ),
            ),
            manage_components.create_actionrow(
                manage_components.create_button(
                    custom_id="7",
                    style=ButtonStyle.blue,
                    label="7",
                ),
                manage_components.create_button(
                    custom_id="8",
                    style=ButtonStyle.blue,
                    label="8",
                ),
                manage_components.create_button(
                    custom_id="9",
                    style=ButtonStyle.blue,
                    label="9",
                ),
                manage_components.create_button(
                    custom_id="*",
                    style=ButtonStyle.green,
                    label="*",
                ),
            ),
            manage_components.create_actionrow(
                manage_components.create_button(
                    custom_id="4",
                    style=ButtonStyle.blue,
                    label="4",
                ),
                manage_components.create_button(
                    custom_id="5",
                    style=ButtonStyle.blue,
                    label="5",
                ),
                manage_components.create_button(
                    custom_id="6",
                    style=ButtonStyle.blue,
                    label="6",
                ),
                manage_components.create_button(
                    custom_id="-",
                    style=ButtonStyle.green,
                    label="-",
                ),
            ),
            manage_components.create_actionrow(
                manage_components.create_button(
                    custom_id="1",
                    style=ButtonStyle.blue,
                    label="1",
                ),
                manage_components.create_button(
                    custom_id="2",
                    style=ButtonStyle.blue,
                    label="2",
                ),
                manage_components.create_button(
                    custom_id="3",
                    style=ButtonStyle.blue,
                    label="3",
                ),
                manage_components.create_button(
                    custom_id="+",
                    style=ButtonStyle.green,
                    label="+",
                ),
            ),
            manage_components.create_actionrow(
                manage_components.create_button(
                    custom_id="(-)",
                    style=ButtonStyle.blue,
                    label="(-)",
                ),
                manage_components.create_button(
                    custom_id="0",
                    style=ButtonStyle.blue,
                    label="0",
                ),
                manage_components.create_button(
                    custom_id=".",
                    style=ButtonStyle.blue,
                    label=".",
                ),
                manage_components.create_button(
                    custom_id="=",
                    style=ButtonStyle.green,
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
            embed = embed_message(
                f"{self.ctx.author.display_name}'s Calculator",
                f"```{text}```"
            )
            self.message = await self.ctx.send(components=self.buttons, embed=embed)
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
                    embed.description = (
                        text if text != "``````" else "```Please Input Your Equation```"
                    )

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
                await button_ctx.edit_origin(components=self.buttons, embed=embed)
            else:
                await self.message.edit(components=self.buttons, embed=embed)

    # checks that the button press author is the same as the message command invoker and that the message matches
    def check_author_and_message(self, ctx: ComponentContext):
        return (ctx.author == self.ctx.author) and (
            self.ctx.message.id == ctx.origin_message.id
        )

    # wait for button press look
    async def wait_for_button_press(self):
        # wait 60s for button press
        try:
            button_ctx: ComponentContext = await manage_components.wait_for_component(
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
