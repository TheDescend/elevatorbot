from apscheduler.schedulers.asyncio import AsyncIOScheduler
from naff import AutocompleteContext, ComponentContext, InteractionContext, ModalContext, PrefixedContext

from ElevatorBot.discordEvents.errorEvents import CustomErrorClient


class ElevatorClient(CustomErrorClient):
    # register the scheduler for easier access
    scheduler = AsyncIOScheduler(timezone="UTC")


# redefine the context to include proper custom subclass type hinting
class ElevatorInteractionContext(InteractionContext):
    @property
    def bot(self) -> ElevatorClient:
        return self._client  # noqa

    @property
    def client(self) -> ElevatorClient:
        return self._client  # noqa


class ElevatorPrefixedContext(PrefixedContext):
    @property
    def bot(self) -> ElevatorClient:
        return self._client  # noqa

    @property
    def client(self) -> ElevatorClient:
        return self._client  # noqa


class ElevatorComponentContext(ComponentContext):
    @property
    def bot(self) -> ElevatorClient:
        return self._client  # noqa

    @property
    def client(self) -> ElevatorClient:
        return self._client  # noqa


class ElevatorAutocompleteContext(AutocompleteContext):
    @property
    def bot(self) -> ElevatorClient:
        return self._client  # noqa

    @property
    def client(self) -> ElevatorClient:
        return self._client  # noqa


class ElevatorModalContext(ModalContext):
    @property
    def bot(self) -> ElevatorClient:
        return self._client  # noqa

    @property
    def client(self) -> ElevatorClient:
        return self._client  # noqa
