from dis_snek.models import ComponentContext

from Backend.database.models import Poll
from ElevatorBot.backendNetworking.misc.polls import BackendPolls


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
