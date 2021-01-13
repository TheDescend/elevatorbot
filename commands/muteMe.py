import asyncio

from commands.base_command import BaseCommand
from functions.roles import assignRolesToUser, removeRolesFromUser
from static.globals import muted_role_id


class muteMe(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "I wonder what this does..."
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, mentioned_user, client):
        await message.channel.send("If you insist...")
        if message.author.id is not mentioned_user.id:
            await message.channel.send("I saw what you did there, that doesn't work here mate")
        await message.author.send("I hope you enjoy your new role, the trial automatically ends after an half an hour 🙃")

        # add muted role
        await assignRolesToUser([muted_role_id], message.author, message.guild)

        # remove muted role after an hour
        await asyncio.sleep(60 * 30)
        await removeRolesFromUser([muted_role_id], message.author, message.guild)
