import dataclasses
from typing import Optional, Type, TypeVar

from dis_snek.models import Embed, InteractionContext
from pydantic import BaseModel
from typing_extensions import Protocol

from ElevatorBot.backendNetworking.errorCodesAndResponses import (
    error_codes_and_responses,
)
from ElevatorBot.misc.formating import embed_message

SchemaType = TypeVar("SchemaType", bound=BaseModel)


@dataclasses.dataclass()
class BackendResult:
    """Holds the return info"""

    success: bool
    result: Optional[SchemaType | dict]
    error: Optional[str]

    __error_message: str = None

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

        # todo go through all usages and check when we send hidden and when not and make that consistent

        # format it
        if format_kwargs:
            self.error_message = format_kwargs

        await ctx.send(ephemeral=hidden, embeds=self.embed)
