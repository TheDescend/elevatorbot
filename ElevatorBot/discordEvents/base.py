from discord.ext.commands import Bot
from discord_slash import SlashCommand

from ElevatorBot.discordEvents.errorEvents import (
    on_component_callback_error,
    on_slash_command_error,
)
from ElevatorBot.discordEvents.guildEvents import (
    on_guild_channel_create,
    on_guild_channel_delete,
    on_guild_channel_update,
    on_guild_join,
    on_guild_remove,
    on_guild_role_delete,
    on_guild_role_update,
)
from ElevatorBot.discordEvents.interactionCallbacks import poll
from ElevatorBot.discordEvents.interactionEvents import on_component, on_slash_command
from ElevatorBot.discordEvents.memberEvents import (
    on_member_join,
    on_member_remove,
    on_member_update,
)
from ElevatorBot.discordEvents.messageEvents import (
    on_message,
    on_message_delete,
    on_message_edit,
    on_reaction_add,
    on_reaction_remove,
)
from ElevatorBot.discordEvents.voiceEvents import on_voice_state_update


def register_discord_events(client: Bot, slash_client: SlashCommand):
    """Import all events and add then to the bot"""

    # error handling
    client.add_listener(on_slash_command_error)
    client.add_listener(on_component_callback_error)

    # interactions logging
    client.add_listener(on_slash_command)
    client.add_listener(on_component)

    # message events
    client.add_listener(on_message)
    client.add_listener(on_message_delete)
    client.add_listener(on_message_edit)
    client.add_listener(on_reaction_add)
    client.add_listener(on_reaction_remove)

    # member events
    client.add_listener(on_member_join)
    client.add_listener(on_member_remove)
    client.add_listener(on_member_update)

    # guild events
    client.add_listener(on_guild_channel_delete)
    client.add_listener(on_guild_channel_create)
    client.add_listener(on_guild_channel_update)
    client.add_listener(on_guild_join)
    client.add_listener(on_guild_remove)
    client.add_listener(on_guild_role_delete)
    client.add_listener(on_guild_role_update)

    # voice events
    client.add_listener(on_voice_state_update)

    # add the component callbacks
    slash_client.add_component_callback(poll)
