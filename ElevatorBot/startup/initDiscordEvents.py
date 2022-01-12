from dis_snek import Listener

from ElevatorBot.discordEvents.base import ElevatorSnake
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
from ElevatorBot.discordEvents.memberEvents import on_member_add, on_member_remove, on_member_update
from ElevatorBot.discordEvents.messageEvents import on_message_create, on_message_delete, on_message_update
from ElevatorBot.discordEvents.voiceEvents import on_voice_state_update


def register_discord_events(client: ElevatorSnake):
    """Import all events and add then to the bot"""

    # message events
    client.add_listener(Listener(func=on_message_create, event="message_create"))
    client.add_listener(Listener(func=on_message_delete, event="message_delete"))
    client.add_listener(Listener(func=on_message_update, event="message_update"))

    # member events
    client.add_listener(Listener(func=on_member_add, event="member_add"))
    client.add_listener(Listener(func=on_member_remove, event="member_remove"))
    client.add_listener(Listener(func=on_member_update, event="member_update"))

    # guild events
    client.add_listener(Listener(func=on_channel_delete, event="channel_delete"))
    client.add_listener(Listener(func=on_channel_create, event="channel_create"))
    client.add_listener(Listener(func=on_channel_update, event="channel_update"))
    client.add_listener(Listener(func=on_guild_join, event="guild_join"))
    client.add_listener(Listener(func=on_guild_left, event="guild_left"))
    client.add_listener(Listener(func=on_role_delete, event="role_delete"))
    client.add_listener(Listener(func=on_role_update, event="role_update"))
    client.add_listener(Listener(func=on_thread_create, event="thread_create"))
    client.add_listener(Listener(func=on_thread_update, event="thread_update"))
    client.add_listener(Listener(func=on_thread_delete, event="thread_delete"))

    # voice events
    client.add_listener(Listener(func=on_voice_state_update, event="voice_state_update"))
