from commands.base_command          import BaseCommand

from functions.dataTransformation   import hasCollectible
from functions.database             import lookupDestinyID

from concurrent.futures             import ThreadPoolExecutor, as_completed
from os                             import cpu_count

class listHasCollectible(BaseCommand):
    def __init__(self):
        # A quick description for the help message
        description = "Lists all players in the clan that own a certain collecTible"
        params = ['collectibleHash']
        topic = "Destiny"
        super().__init__(description, params, topic)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        async with message.channel.typing():
            collectibleHash = params[0]
            future_to_did = {}
            ownedby = []
            with ThreadPoolExecutor(max_workers=cpu_count() * 5) as executor:
                # Start the load operations and mark each future with its URL
                for discordUser in message.guild.members:
                    destinyID = lookupDestinyID(discordUser.id)
                    if destinyID:
                        future_to_did[executor.submit(hasCollectible, destinyID, collectibleHash)] = discordUser.name

                for future in as_completed(future_to_did):
                    if future.result():
                        ownedby.append(future_to_did[future])
            await message.channel.send(f'That collectible is in the hands of {", ".join(ownedby)}')
