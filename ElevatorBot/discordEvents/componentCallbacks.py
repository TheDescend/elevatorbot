from dis_snek import Snake
from dis_snek.models import ComponentCommand, ComponentContext

from Backend.database.models import Poll
from ElevatorBot.backendNetworking.misc.polls import BackendPolls


class ComponentCallbacks:
    @staticmethod
    async def poll(ctx: ComponentContext):
        """Handles when a component with the custom_id 'poll' gets interacted with"""

        backend = BackendPolls(ctx=ctx, discord_member=ctx.author, guild=ctx.guild)
        backend.hidden = True

        # get the id from the embed
        poll_id = int(ctx.message.embeds[0].footer.text.split("|")[1].removeprefix("  ID: "))

        # inform the db that sb voted
        result = await backend.user_input(poll_id=poll_id, choice_name=ctx.values[0])

        if not result:
            return

        # create a poll obj from that data
        poll_obj = await Poll.from_dict(client=ctx.bot, data=result)
        await poll_obj.send(ctx)  # todo

    @staticmethod
    async def registration(ctx: ComponentContext):
        """Handles when a component with the custom_id 'registration' gets interacted with"""

        # todo
        ...

    @staticmethod
    async def other_game_roles(ctx: ComponentContext):
        """Handles when a component with the custom_id 'other_game_roles' gets interacted with"""

        # todo
        ...

    @staticmethod
    async def increment_button(ctx: ComponentContext):
        """Handles when a component with the custom_id 'increment_button' gets interacted with"""

        # todo
        ...

    @staticmethod
    async def lfg_join(ctx: ComponentContext):
        """Handles when a component with the custom_id 'lfg_join' gets interacted with"""

        # todo
        ...

    @staticmethod
    async def lfg_leave(ctx: ComponentContext):
        """Handles when a component with the custom_id 'lfg_leave' gets interacted with"""

        # todo
        ...

    @staticmethod
    async def lfg_backup(ctx: ComponentContext):
        """Handles when a component with the custom_id 'lfg_backup' gets interacted with"""

        # todo
        ...

    @staticmethod
    async def clan_join_request(ctx: ComponentContext):
        """Handles when a component with the custom_id 'clan_join_request' gets interacted with"""

        # todo
        ...


def add_component_callbacks(client: Snake):
    """Add global custom component callbacks"""

    # get all functions from the class. Magic
    for custom_id in [k for k in ComponentCallbacks.__dict__ if not k.startswith("__")]:
        client.add_component_callback(
            ComponentCommand(
                name=f"ComponentCallback::{custom_id}",
                callback=getattr(ComponentCallbacks, custom_id),
                listeners=[custom_id],
            )
        )
