import dataclasses

from dis_snek.models import Embed
from dis_snek.models import InteractionContext

from ElevatorBot.misc.formating import embed_message
from ElevatorBot.static.errorCodesAndResponses import error_codes_and_responses


@dataclasses.dataclass
class BackendResult:
    """Holds the return info"""

    success: bool
    result: dict = None
    error: str = None

    __error_message: str = dataclasses.field(default=None, init=False, repr=False, compare=False)

    def __bool__(self):
        return self.success

    @property
    def embed(self) -> Embed:
        """ " Returns a nicely formatted embed, which can be returned to the user"""

        return embed_message(title="Error", description=self.error_message)

    @property
    def error_message(self) -> str:
        """Returns the corresponding error message for the error"""

        if not self.__error_message:
            if not self.error:
                self.__error_message = "Success"

            if self.error in error_codes_and_responses:
                self.__error_message = error_codes_and_responses[self.error]
            else:
                self.__error_message = "Something went wrong"

        return self.__error_message

    @error_message.setter
    def error_message(self, kwargs: dict):
        """Formats the error message. See error_codes_and_responses"""

        self.__error_message = self.error_message.format(**kwargs)

    async def send_error_message(
        self,
        ctx: InteractionContext,
        hidden: bool = False,
        **format_kwargs,
    ):
        """Sends the error message. format_kwargs are used to format the message before sending it"""

        # format it
        if format_kwargs:
            self.error_message = format_kwargs

        await ctx.send(ephemeral=hidden, embeds=self.embed)
