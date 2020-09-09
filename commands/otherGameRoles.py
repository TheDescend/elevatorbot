from commands.base_command  import BaseCommand

import discord

gta_id = 709120893728718910
barotrauma_id = 738438622553964636
valorant_id = 709378171832893572
amongUs_id = 750409552075423753

class gta(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Get / loose game role"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        roles = [role.id for role in message.author.roles]
        if gta_id not in roles:
            await message.author.add_roles(discord.utils.get(message.guild.roles, id=gta_id))
            await message.add_reaction("✅")
        else:
            await message.author.remove_roles(discord.utils.get(message.guild.roles, id=gta_id))
            await message.add_reaction("❌")

class barotrauma(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Get / loose game role"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        roles = [role.id for role in message.author.roles]
        if barotrauma_id not in roles:
            await message.author.add_roles(discord.utils.get(message.guild.roles, id=barotrauma_id))
            await message.add_reaction("✅")
        else:
            await message.author.remove_roles(discord.utils.get(message.guild.roles, id=barotrauma_id))
            await message.add_reaction("❌")

class valorant(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Get / loose game role"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        roles = [role.id for role in message.author.roles]
        if valorant_id not in roles:
            await message.author.add_roles(discord.utils.get(message.guild.roles, id=valorant_id))
            await message.add_reaction("✅")
        else:
            await message.author.remove_roles(discord.utils.get(message.guild.roles, id=valorant_id))
            await message.add_reaction("❌")

class amongUs(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Get / loose game role"
        params = []
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        roles = [role.id for role in message.author.roles]
        if amongUs_id not in roles:
            await message.author.add_roles(discord.utils.get(message.guild.roles, id=amongUs_id))
            await message.add_reaction("✅")
        else:
            await message.author.remove_roles(discord.utils.get(message.guild.roles, id=amongUs_id))
            await message.add_reaction("❌")

