from typing import TYPE_CHECKING

from naff import AutocompleteContext, ComponentContext, InteractionContext, ModalContext, PrefixedContext

if TYPE_CHECKING:
    from ElevatorBot.discordEvents.base import ElevatorClient


# redefine the context to include proper custom subclass type hinting
class ElevatorInteractionContext(InteractionContext):
    @property
    def bot(self) -> "ElevatorClient":
        return self._client  # noqa

    @property
    def client(self) -> "ElevatorClient":
        return self._client  # noqa


class ElevatorPrefixedContext(PrefixedContext):
    @property
    def bot(self) -> "ElevatorClient":
        return self._client  # noqa

    @property
    def client(self) -> "ElevatorClient":
        return self._client  # noqa


class ElevatorComponentContext(ComponentContext):
    @property
    def bot(self) -> "ElevatorClient":
        return self._client  # noqa

    @property
    def client(self) -> "ElevatorClient":
        return self._client  # noqa


class ElevatorAutocompleteContext(AutocompleteContext):
    @property
    def bot(self) -> "ElevatorClient":
        return self._client  # noqa

    @property
    def client(self) -> "ElevatorClient":
        return self._client  # noqa


class ElevatorModalContext(ModalContext):
    @property
    def bot(self) -> "ElevatorClient":
        return self._client  # noqa

    @property
    def client(self) -> "ElevatorClient":
        return self._client  # noqa
