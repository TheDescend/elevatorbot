from dis_snek.client import Snake
from dis_snek.models import InteractionContext
from dis_snek.models import Scale


class BaseScale(Scale):
    """Overwrites default events like on_error and pre_run"""

    def __init__(self, client):
        self.client: Snake = client
        self.add_scale_prerun(self.default_pre_run)

    async def default_pre_run(self, ctx: InteractionContext):
        """
        Default command that is run before the command is handled
        Checks if the member is registered
        """

        # todo
        ...
