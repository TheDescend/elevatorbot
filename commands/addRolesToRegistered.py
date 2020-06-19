from commands.base_command  import BaseCommand
from functions.roles        import assignRolesToUser, removeRolesFromUser
from functions.database     import getToken



class addRolesToRegistered(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Assigns @Registered or @Not Registered to everyone"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        for member in message.guild.members:
            await removeRolesFromUser(["Registered"], member, message.guild)
            await removeRolesFromUser(["Not Registered"], member, message.guild)

            if getToken(member.id):
                await assignRolesToUser(["Registered"], member, message.guild)
            else:
                await assignRolesToUser(["Not Registered"], member, message.guild)

        await message.channel.send("Done")


class whoIsNotRegistered(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Assigns @Registered or @Not Registered to everyone"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        for member in message.guild.members:
            if not getToken(member.id):
                await message.channel.send(member.name)