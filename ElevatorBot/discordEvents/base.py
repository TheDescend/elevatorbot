from dis_snek.client import Snake
from dis_snek.models import Listener

from ElevatorBot.discordEvents.guildEvents import (
    on_channel_create,
    on_channel_delete,
    on_channel_update,
    on_guild_join,
    on_guild_left,
    on_role_delete,
    on_role_update,
    on_thread_create,
    on_thread_delete,
    on_thread_update,
)
from ElevatorBot.discordEvents.memberEvents import (
    on_member_add,
    on_member_remove,
    on_member_update,
)
from ElevatorBot.discordEvents.messageEvents import (
    on_message_create,
    on_message_delete,
    on_message_edit,
)


def register_discord_events(client: Snake):
    """Import all events and add then to the bot"""

    # message events
    client.add_listener(Listener(on_message_create, "message_create"))
    client.add_listener(Listener(on_message_delete, "message_delete"))
    client.add_listener(Listener(on_message_edit, "message_edit"))

    # member events
    client.add_listener(Listener(on_member_add, "member_add"))
    client.add_listener(Listener(on_member_remove, "member_remove"))
    client.add_listener(Listener(on_member_update, "member_update"))

    # guild events
    client.add_listener(Listener(on_channel_delete, "channel_delete"))
    client.add_listener(Listener(on_channel_create, "channel_create"))
    client.add_listener(Listener(on_channel_update, "channel_update"))
    client.add_listener(Listener(on_guild_join, "guild_join"))
    client.add_listener(Listener(on_guild_left, "guild_left"))
    client.add_listener(Listener(on_role_delete, "role_delete"))
    client.add_listener(Listener(on_role_update, "role_update"))
    client.add_listener(Listener(on_thread_create, "thread_create"))
    client.add_listener(Listener(on_thread_update, "thread_update"))
    client.add_listener(Listener(on_thread_delete, "thread_delete"))

    # # voice events
    # client.add_listener(Listener(on_voice_state_update, "voice_state_update"))  # todo currently missing
    #
    # # add the component callbacks
    # # slash_client.add_component_callback(poll)   # todo currently missing
