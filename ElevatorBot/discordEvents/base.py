from dis_snek.client import Snake
from dis_snek.models import Listener

from ElevatorBot.discordEvents.errorEvents import on_component_callback_error
from ElevatorBot.discordEvents.errorEvents import on_slash_command_error
from ElevatorBot.discordEvents.guildEvents import on_channel_create
from ElevatorBot.discordEvents.guildEvents import on_channel_delete
from ElevatorBot.discordEvents.guildEvents import on_channel_update
from ElevatorBot.discordEvents.guildEvents import on_guild_join
from ElevatorBot.discordEvents.guildEvents import on_guild_remove
from ElevatorBot.discordEvents.guildEvents import on_guild_role_delete
from ElevatorBot.discordEvents.guildEvents import on_guild_role_update
from ElevatorBot.discordEvents.guildEvents import on_thread_create
from ElevatorBot.discordEvents.guildEvents import on_thread_delete
from ElevatorBot.discordEvents.guildEvents import on_thread_update
from ElevatorBot.discordEvents.interactionCallbacks import poll
from ElevatorBot.discordEvents.interactionEvents import on_component
from ElevatorBot.discordEvents.interactionEvents import on_slash_command
from ElevatorBot.discordEvents.memberEvents import on_member_add
from ElevatorBot.discordEvents.memberEvents import on_member_remove
from ElevatorBot.discordEvents.memberEvents import on_member_update
from ElevatorBot.discordEvents.messageEvents import on_message
from ElevatorBot.discordEvents.messageEvents import on_message_delete
from ElevatorBot.discordEvents.messageEvents import on_message_edit
from ElevatorBot.discordEvents.voiceEvents import on_voice_state_update


def register_discord_events(client: Snake):
    """Import all events and add then to the bot"""

    # error handling
    client.add_listener(Listener(on_slash_command_error, "slash_command_error"))  # todo currently missing
    client.add_listener(Listener(on_component_callback_error, "component_callback_error"))  # todo currently missing

    # interactions logging
    client.add_listener(Listener(on_slash_command, "interaction_create"))
    client.add_listener(Listener(on_component, "component"))

    # message events
    client.add_listener(Listener(on_message, "message"))
    client.add_listener(Listener(on_message_delete, "message_delete"))
    client.add_listener(Listener(on_message_edit, "message_edit"))
    client.add_listener(Listener(on_reaction_add, "reaction_add"))
    client.add_listener(Listener(on_reaction_remove, "reaction_remove"))

    # member events
    client.add_listener(Listener(on_member_add, "member_add"))
    client.add_listener(Listener(on_member_remove, "member_remove"))
    client.add_listener(Listener(on_member_update, "member_update"))

    # guild events
    client.add_listener(Listener(on_channel_delete, "channel_delete"))
    client.add_listener(Listener(on_channel_create, "channel_create"))
    client.add_listener(Listener(on_channel_update, "channel_update"))
    client.add_listener(Listener(on_guild_join, "guild_join"))
    client.add_listener(Listener(on_guild_remove, "guild_remove"))
    client.add_listener(Listener(on_guild_role_delete, "guild_role_delete"))  # todo currently missing
    client.add_listener(Listener(on_guild_role_update, "guild_role_update"))  # todo currently missing
    client.add_listener(Listener(on_thread_create, "thread_create"))
    client.add_listener(Listener(on_thread_update, "thread_update"))
    client.add_listener(Listener(on_thread_delete, "thread_delete"))

    # voice events
    client.add_listener(Listener(on_voice_state_update, "voice_state_update"))  # todo currently missing

    # add the component callbacks
    slash_client.add_component_callback(poll)
