import logging

from dis_snek.models import ComponentContext, InteractionContext


async def on_slash_command(ctx: InteractionContext):
    """Gets triggered every slash command"""

    # print the command
    print (f"{ctx.author.display_name} used '/{ctx.name}' with kwargs '{ctx.kwargs}'")

    # log the command
    logger = logging.getLogger("commands")
    logger.info(
        f"InteractionID '{ctx.interaction_id}' - User '{ctx.author.name}' with discordID '{ctx.author.id}' executed '/{ctx.name}' with kwargs '{ctx.kwargs}' in guildID '{ctx.guild.id}', channelID '{ctx.channel.id}'"
    )


async def on_component(ctx: ComponentContext):
    """Gets triggered on every component usage"""

    # log the command
    logger = logging.getLogger("interactions")
    logger.info(
        f"InteractionID '{ctx.interaction_id}' - User '{ctx.author.name}' with discordID '{ctx.author.id}' clicked on componentType '{ctx.component_type}', componentID '{ctx.component_id}' in guildID '{ctx.origin_message.guild.id}', channelID '{ctx.origin_message.channel.id}', messageID '{ctx.origin_message.id}'"
    )
