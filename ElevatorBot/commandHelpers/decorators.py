from dis_snek.models import InteractionContext

from ElevatorBot.misc.formating import embed_message


def has_user_option_permission(func):
    async def wrapper(ctx: InteractionContext, **kwargs):
        if "user" in kwargs:
            # check if author has elevated permissions in guild
            # todo do that by getting the setup role from the db
            if kwargs["user"] != ctx.author:
                pass
                # if "cool permission" not in ctx.author.roles:
                #     await ctx.send(hidden=True, embed=embed_message(
                #         "Error",
                #         "You do not have permission to use the `user` argument\nPlease try again without it"
                #     ))
                #     return
        return await func(ctx, **kwargs)

    return wrapper
